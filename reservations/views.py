import secrets
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.models import BusinessConfig, Role
from kitchen.models import Dish

from .models import Reservation, ReservationStatus, Table, TableBlock


# ---------------------------------------------------------------------------
# Portal de reservas (RF-27, RF-28, RF-29)
# ---------------------------------------------------------------------------


def _create_reservation(client_email, client_cedula, guests, tables, start_at, notes):
    """Crea la reserva de 2 horas y marca las mesas (RF-29)."""
    end_at = start_at + timedelta(hours=2)
    reservation = Reservation.objects.create(
        client_email=client_email,
        client_cedula=client_cedula,
        guests=guests,
        start_at=start_at,
        end_at=end_at,
        status=ReservationStatus.RESERVED,
    )
    reservation.tables.set(tables)
    return reservation


def reservation_portal(request):
    """Selección de fecha, bloque, comensales y mesas (RF-27)."""
    if request.method == "POST":
        client_email = request.POST.get("email", "").strip()
        client_cedula = request.POST.get("cedula", "").strip()
        date = request.POST.get("date", "").strip()
        time = request.POST.get("time", "").strip()
        guests_raw = request.POST.get("guests", "").strip()
        table_ids = request.POST.getlist("tables")
        notes = request.POST.get("notes", "").strip()

        config = BusinessConfig.objects.get(pk=1)

        try:
            guests = int(guests_raw)
        except ValueError:
            messages.error(request, "Seleccione el número de comensales.")
            return redirect("reservations:portal")

        # Validación mínima de anticipación (RF-27/RF-29)
        try:
            from datetime import datetime

            start_at = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            start_at = timezone.make_aware(start_at)
        except ValueError:
            messages.error(request, "Fecha u horario inválidos.")
            return redirect("reservations:portal")

        min_hours = config.min_reservation_hours
        if (start_at - timezone.localtime()).total_seconds() < min_hours * 3600:
            messages.error(
                request, f"La reserva requiere mínimo {min_hours} horas de anticipación."
            )
            return redirect("reservations:portal")

        if not table_ids:
            messages.error(request, "Seleccione al menos una mesa.")
            return redirect("reservations:portal")

        tables = list(Table.objects.filter(pk__in=table_ids))
        total_capacity = sum(t.capacity for t in tables)
        if total_capacity < guests:
            messages.error(request, "La capacidad de las mesas no cubre los comensales.")
            return redirect("reservations:portal")

        # Bloqueo de 2 minutos para evitar doble reserva concurrente (RF-28)
        token = secrets.token_hex(16)
        block = TableBlock.objects.create(
            token=token,
            expires_at=timezone.now() + timedelta(minutes=config.table_block_minutes),
        )
        block.tables.set(tables)

        reservation = _create_reservation(
            client_email, client_cedula, guests, tables, start_at, notes
        )
        block.confirmed = True
        block.save(update_fields=["confirmed"])

        messages.success(
            request,
            f"Reserva confirmada: {date} {time} · {guests} comensales · {len(tables)} mesa(s). "
            f"Bloque de 2 horas bajo UTC-5.",
        )
        return redirect("reservations:my_reservations")

    tables = Table.objects.filter(disabled=False)
    dishes = Dish.objects.filter(active=True)[:50]
    return render(request, "reservations/portal.html", {"tables": tables, "dishes": dishes})


# ---------------------------------------------------------------------------
# Mis reservas (RF-32) y cancelación (RF-33)
# ---------------------------------------------------------------------------


@login_required
def my_reservations(request):
    """Muestra las reservas activas del cliente autenticado (RF-32)."""
    user = request.user
    if user.role != Role.CLIENT:
        messages.error(request, "Este portal es para clientes registrados.")
        return redirect(request.user.dashboard_url)

    active = Reservation.objects.filter(
        client_cedula=user.cedula,
        status=ReservationStatus.RESERVED,
    )
    history = Reservation.objects.filter(
        client_cedula=user.cedula,
    ).exclude(status=ReservationStatus.RESERVED)[:20]

    return render(
        request,
        "reservations/my_reservations.html",
        {"active": active, "history": history},
    )


@login_required
def cancel_reservation(request, reservation_id):
    """Cancelación autónoma con >= 4 horas de anticipación (RF-33)."""
    reservation = get_object_or_404(
        Reservation, pk=reservation_id, client_cedula=request.user.cedula
    )

    if not reservation.cancel_allowed():
        messages.error(
            request,
            "No es posible cancelar con menos de 4 horas de anticipación. "
            "Contacte al restaurante directamente.",
        )
        return redirect("reservations:my_reservations")

    reservation.status = ReservationStatus.CANCELLED
    reservation.save(update_fields=["status"])
    messages.success(request, "Reserva cancelada. Las mesas fueron liberadas.")
    return redirect("reservations:my_reservations")


# ---------------------------------------------------------------------------
# API de disponibilidad (croquis) y detalle
# ---------------------------------------------------------------------------


def table_list(request):
    """Estado en tiempo real del croquis de mesas."""
    from django.http import JsonResponse

    now = timezone.now()
    data = []
    for table in Table.objects.filter(disabled=False):
        data.append({
            "id": table.pk,
            "number": table.number,
            "capacity": table.capacity,
            "x": table.x,
            "y": table.y,
            "shape": table.shape,
            "status": table.status,
        })
    return JsonResponse(data, safe=False)


def reservation_detail(request, reservation_id):
    """Detalle JSON de una reserva (para el croquis/consulta)."""
    from django.http import JsonResponse

    reservation = get_object_or_404(Reservation, pk=reservation_id)
    return JsonResponse({
        "id": reservation.pk,
        "email": reservation.client_email,
        "cedula": reservation.client_cedula,
        "guests": reservation.guests,
        "start_at": reservation.start_at.isoformat(),
        "end_at": reservation.end_at.isoformat(),
        "status": reservation.get_status_display(),
        "tables": [t.number for t in reservation.tables.all()],
    })


# ---------------------------------------------------------------------------
# Sala / Mesero: plano de mesas, check-in y no-show (RF-04, RF-30, RF-31)
# ---------------------------------------------------------------------------


def _guard_waiter(request):
    if request.user.role != Role.WAITER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return None


@login_required
def floor_plan(request):
    """Plano de salas del Mesero: estado real de cada mesa (propiedad `status`)."""
    blocked = _guard_waiter(request)
    if blocked:
        return blocked

    from kitchen.models import OrderStatus

    tables = Table.objects.prefetch_related("orders")
    table_rows = []
    for table in tables:
        active_order = table.orders.filter(
            status__in=[
                OrderStatus.WAITING,
                OrderStatus.PREPARING,
                OrderStatus.READY,
            ]
        ).first()
        table_rows.append({
            "table": table,
            "status": table.status,
            "active_order": active_order,
            "has_order": active_order is not None,
        })

    return render(
        request,
        "reservations/floor_plan.html",
        {"tables": table_rows},
    )


@login_required
def checkin(request):
    """Check-in de reserva: valida llegada, actualiza comensales y une mesas (RF-30)."""
    blocked = _guard_waiter(request)
    if blocked:
        return blocked

    reservations = None
    selected = None
    if request.method == "GET" and request.GET.get("cedula"):
        reservations = Reservation.objects.filter(
            client_cedula=request.GET.get("cedula").strip(),
            status__in=[ReservationStatus.RESERVED, ReservationStatus.CONFIRMED],
        )

    if request.method == "POST":
        reservation_id = request.POST.get("reservation_id")
        real_people = request.POST.get("real_people", "").strip()
        table_ids = request.POST.getlist("tables")

        reservation = get_object_or_404(Reservation, pk=reservation_id)
        try:
            people = int(real_people)
            if people <= 0:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, "Ingrese un número de comensales válido.")
            return redirect("reservations:checkin")

        extra = Table.objects.filter(pk__in=table_ids, disabled=False)
        total_capacity = sum(t.capacity for t in reservation.tables.all()) + sum(
            t.capacity for t in extra
        )
        if total_capacity < people:
            messages.error(request, "La capacidad de las mesas no cubre los comensales.")
            return redirect("reservations:checkin")

        reservation.guests = people
        if extra:
            reservation.tables.add(*extra)
        reservation.status = ReservationStatus.CONFIRMED
        reservation.save(update_fields=["guests", "status"])

        from audit.models import ActionType, AuditLog, Result

        AuditLog.log(
            request.user,
            ActionType.CHECK_IN,
            Result.SUCCESS,
            object_type="Reservation",
            object_id=reservation.pk,
            detail=f"Check-in de {people} comensales en {total_capacity} pax.",
        )
        messages.success(request, "Check-in registrado. Las mesas quedaron ocupadas.")
        return redirect("reservations:checkin")

    return render(
        request,
        "reservations/checkin.html",
        {"reservations": reservations, "tables": Table.objects.filter(disabled=False)},
    )


@login_required
def no_show(request):
    """Registra no-show tras la tolerancia de 15 min (RF-04, RF-31)."""
    blocked = _guard_waiter(request)
    if blocked:
        return blocked

    if request.method == "POST":
        reservation_id = request.POST.get("reservation_id")
        reservation = get_object_or_404(Reservation, pk=reservation_id)
        try:
            reservation.register_no_show()
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("reservations:checkin")

        from audit.models import ActionType, AuditLog, Result

        AuditLog.log(
            request.user,
            ActionType.NO_SHOW,
            Result.SUCCESS,
            object_type="Reservation",
            object_id=reservation.pk,
            detail=f"No-show de {reservation.client_email} (mesa {reservation.start_at:%H:%M} UTC-5).",
        )
        messages.success(request, "No-show registrado. Las mesas quedaron disponibles.")
        return redirect("reservations:checkin")

    return redirect("reservations:checkin")