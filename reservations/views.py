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


def menu_public(request):
    """Carta pública del restaurante — link compartible para QR/menú digital (RF-13/14).

    Pública sin login, lista todos los platillos activos con precio USD.
    URL: /reservas/menu/
    """
    dishes = Dish.objects.filter(active=True).order_by("name")
    return render(request, "reservations/menu.html", {"dishes": dishes})


# ---------------------------------------------------------------------------
# Helpers flujo Luxe (menú → login/registro → reserva en 3 pasos)
# ---------------------------------------------------------------------------

def _require_client(request):
    """Guard para flujo de reserva: solo CLIENT autenticado."""
    if not request.user.is_authenticated:
        return redirect(f"{redirect('reservations:client_login').url}?next={request.path}")
    if request.user.role != Role.CLIENT:
        messages.error(request, "Este portal es solo para clientes.")
        return redirect(request.user.dashboard_url)
    return None


def _get_session_data(request):
    return request.session.get("reservation_flow", {})


def _set_session_data(request, data):
    request.session["reservation_flow"] = data
    request.session.modified = True


def _clear_session_data(request):
    if "reservation_flow" in request.session:
        del request.session["reservation_flow"]
        request.session.modified = True


def _available_tables_for(start_at, end_at):
    """Devuelve mesas disponibles para el bloque [start_at, end_at)."""
    # Mesas no deshabilitadas y sin reserva solapada RESERVED/CONFIRMED
    reserved_ids = set(
        Reservation.objects.filter(
            status__in=[ReservationStatus.RESERVED, ReservationStatus.CONFIRMED],
            start_at__lt=end_at,
            end_at__gt=start_at,
        ).values_list("tables__id", flat=True)
    )
    # Bloqueos activos
    from django.utils import timezone as _tz
    blocked_ids = set(
        TableBlock.objects.filter(confirmed=False, expires_at__gt=_tz.now()).values_list("tables__id", flat=True)
    )
    tables = Table.objects.filter(disabled=False)
    # Anotar disponibilidad
    for t in tables:
        t.is_reserved = t.pk in reserved_ids
        t.is_blocked = t.pk in blocked_ids
    return tables


def reservation_portal(request):
    """Paso 1 Luxe: selección de fecha, hora y comensales — requiere CLIENT login.

    Soporta flujo legacy de tests (POST con tables directo → crea reserva en 1 paso)
    además del flujo Luxe en 3 pasos (sin tables → guarda sesión y va a mesas).
    """
    # Guard Luxe: menú → login → reserva
    if not request.user.is_authenticated:
        return redirect(f"/reservas/login/?next=/reservas/")
    if request.user.role != Role.CLIENT:
        messages.error(request, "Este portal es solo para clientes.")
        return redirect(request.user.dashboard_url)

    config = BusinessConfig.objects.get(pk=1)

    if request.method == "POST":
        date = request.POST.get("date", "").strip()
        time = request.POST.get("time", "").strip()
        guests_raw = request.POST.get("guests", "").strip()

        try:
            guests = int(guests_raw)
            if guests < 1 or guests > 20:
                raise ValueError
        except ValueError:
            messages.error(request, "Ingrese el número de comensales (1 a 20).")
            return redirect("reservations:portal")

        try:
            from datetime import datetime
            start_at = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            start_at = timezone.make_aware(start_at)
        except ValueError:
            messages.error(request, "Fecha u horario inválidos.")
            return redirect("reservations:portal")

        # Validar anticipación y horario operativo 10:00-00:00
        min_hours = config.min_reservation_hours
        if (start_at - timezone.localtime()).total_seconds() < min_hours * 3600:
            messages.error(request, f"La reserva requiere mínimo {min_hours} horas de anticipación (UTC-5).")
            return redirect("reservations:portal")

        # Horario 10:00-00:00 — interpretar 00:00 como fin de día siguiente
        t = start_at.time()
        if not (t >= config.operating_start or t == config.operating_end):
            if t < config.operating_start and t.hour != 0:
                messages.error(request, "Horario fuera de operación (10:00 – 00:00 UTC-5).")
                return redirect("reservations:portal")

        # Compatibilidad legacy: si el POST trae tables, crea la reserva directo (tests)
        legacy_table_ids = request.POST.getlist("tables") or ([request.POST.get("tables")] if request.POST.get("tables") else [])
        legacy_table_ids = [tid for tid in legacy_table_ids if tid]
        if legacy_table_ids:
            tables = list(Table.objects.filter(pk__in=legacy_table_ids, disabled=False))
            if not tables:
                messages.error(request, "Mesas no válidas.")
                return redirect("reservations:portal")
            total_capacity = sum(x.capacity for x in tables)
            if total_capacity < guests:
                messages.error(request, f"La capacidad ({total_capacity}) no cubre {guests} comensales.")
                return redirect("reservations:portal")
            # Validar solape simple
            end_at = start_at + timedelta(hours=2)
            reserved_ids = set(Reservation.objects.filter(
                status__in=[ReservationStatus.RESERVED, ReservationStatus.CONFIRMED],
                start_at__lt=end_at, end_at__gt=start_at,
            ).values_list("tables__id", flat=True))
            for tid in legacy_table_ids:
                if int(tid) in reserved_ids:
                    messages.error(request, "Una de las mesas ya está reservada en ese bloque de 2 horas.")
                    return redirect("reservations:portal")
            email = request.POST.get("email", "").strip() or request.user.email
            cedula = request.POST.get("cedula", "").strip() or (request.user.cedula or "")
            notes = request.POST.get("notes", "").strip()
            reservation = _create_reservation(client_email=email, client_cedula=cedula, guests=guests, tables=tables, start_at=start_at, notes=notes)
            reservation.client = request.user
            reservation.save(update_fields=["client"])
            messages.success(request, f"Reserva confirmada LX-{reservation.pk:04d}: {date} {time} · {guests} comensales.")
            return redirect("reservations:my_reservations")

        _set_session_data(request, {"date": date, "time": time, "guests": guests})
        return redirect("reservations:table_select")

    # GET: mostrar paso 1 con calendario Luxe
    return render(request, "reservations/step1_details.html", {"config": config})


@login_required
def reservation_tables(request):
    """Paso 2 Luxe: Selección visual de mesa — requiere sesión paso 1."""
    guard = _require_client(request)
    if guard:
        return guard

    data = _get_session_data(request)
    if not data.get("date") or not data.get("time"):
        messages.error(request, "Complete primero fecha, hora y comensales.")
        return redirect("reservations:portal")

    from datetime import datetime
    start_at = timezone.make_aware(datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M"))
    end_at = start_at + timedelta(hours=2)
    guests = int(data["guests"])
    config = BusinessConfig.objects.get(pk=1)

    if request.method == "POST":
        table_ids = request.POST.getlist("tables") or ([request.POST.get("tables")] if request.POST.get("tables") else [])
        # fallback para selección single via hidden input
        table_ids = [tid for tid in table_ids if tid]
        if not table_ids:
            messages.error(request, "Seleccione al menos una mesa.")
            return redirect("reservations:table_select")

        tables = list(Table.objects.filter(pk__in=table_ids, disabled=False))
        if not tables:
            messages.error(request, "Mesas no válidas.")
            return redirect("reservations:table_select")

        total_capacity = sum(t.capacity for t in tables)
        if total_capacity < guests:
            messages.error(request, f"La capacidad ({total_capacity}) no cubre {guests} comensales.")
            return redirect("reservations:table_select")

        # Validar disponibilidad real (sin solape)
        reserved_ids = set(
            Reservation.objects.filter(
                status__in=[ReservationStatus.RESERVED, ReservationStatus.CONFIRMED],
                start_at__lt=end_at,
                end_at__gt=start_at,
            ).values_list("tables__id", flat=True)
        )
        for tid in table_ids:
            if int(tid) in reserved_ids:
                messages.error(request, "Una de las mesas ya está reservada en ese bloque de 2 horas.")
                return redirect("reservations:table_select")

        _set_session_data(request, {**data, "table_ids": [int(t.pk) for t in tables]})
        return redirect("reservations:confirm")

    tables = _available_tables_for(start_at, end_at)
    from .models import Room
    # Agrupar por sala para plano visual
    rooms = []
    rooms_order = [Room.VIP, Room.TERRAZA, Room.PISO_1]
    room_labels = dict(Room.choices)
    for room_code in rooms_order:
        room_tables = [t for t in tables if t.room == room_code]
        rooms.append({
            "code": room_code,
            "label": room_labels[room_code],
            "tables": room_tables,
        })
    return render(request, "reservations/step2_tables.html", {
        "tables": tables,
        "rooms": rooms,
        "guests": guests,
        "date": data["date"],
        "time": data["time"],
        "start_at": start_at,
        "end_at": end_at,
    })


@login_required
def reservation_confirm(request):
    """Paso 3 Luxe: Confirmación con datos del cliente y creación final (RF-29)."""
    guard = _require_client(request)
    if guard:
        return guard

    data = _get_session_data(request)
    if not data.get("table_ids") or not data.get("date"):
        messages.error(request, "Complete los pasos anteriores.")
        return redirect("reservations:portal")

    from datetime import datetime
    start_at = timezone.make_aware(datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M"))
    end_at = start_at + timedelta(hours=2)
    guests = int(data["guests"])
    tables = list(Table.objects.filter(pk__in=data["table_ids"]))

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip() or f"{request.user.first_name} {request.user.last_name}".strip()
        email = request.POST.get("email", "").strip() or request.user.email
        phone = request.POST.get("phone", "").strip()
        notes = request.POST.get("notes", "").strip()

        if not email:
            messages.error(request, "El correo es obligatorio.")
            return redirect("reservations:confirm")

        config = BusinessConfig.objects.get(pk=1)
        # Revalidar anticipación por si pasó tiempo
        if (start_at - timezone.localtime()).total_seconds() < config.min_reservation_hours * 3600:
            messages.error(request, "La reserva ya no cumple la anticipación mínima.")
            _clear_session_data(request)
            return redirect("reservations:portal")

        # Bloqueo 2 min (RF-28)
        token = secrets.token_hex(16)
        block = TableBlock.objects.create(
            token=token,
            expires_at=timezone.now() + timedelta(minutes=config.table_block_minutes),
        )
        block.tables.set(tables)

        reservation = _create_reservation(
            client_email=email,
            client_cedula=request.user.cedula or "",
            guests=guests,
            tables=tables,
            start_at=start_at,
            notes=notes,
        )
        # Vincular al usuario cliente
        reservation.client = request.user
        reservation.save(update_fields=["client"])
        block.confirmed = True
        block.save(update_fields=["confirmed"])
        _clear_session_data(request)

        messages.success(request, f"Reserva confirmada LX-{reservation.pk:04d}: {data['date']} {data['time']} · {guests} comensales.")
        return redirect("reservations:success", reservation_id=reservation.pk)

    # Prefill con datos del usuario
    initial = {
        "full_name": f"{request.user.first_name} {request.user.last_name}".strip(),
        "email": request.user.email,
        "phone": "",
    }
    return render(request, "reservations/step3_confirm.html", {
        "tables": tables,
        "guests": guests,
        "date": data["date"],
        "time": data["time"],
        "start_at": start_at,
        "end_at": end_at,
        "initial": initial,
    })


@login_required
def reservation_success(request, reservation_id):
    """Pantalla de éxito tras confirmar — muestra referencia LX-XXXX."""
    guard = _require_client(request)
    if guard:
        return guard
    reservation = get_object_or_404(Reservation, pk=reservation_id, client=request.user)
    return render(request, "reservations/success.html", {"reservation": reservation})


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

    data = []
    for table in Table.objects.filter(disabled=False):
        data.append({
            "id": table.pk,
            "number": table.number,
            "capacity": table.capacity,
            "room": table.room,
            "room_display": table.get_room_display(),
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
    """Plano de salas del Mesero: estado real de cada mesa por sala (propiedad `status`)."""
    blocked = _guard_waiter(request)
    if blocked:
        return blocked

    from kitchen.models import OrderStatus

    from .models import Room

    tables = Table.objects.prefetch_related("orders").order_by("room", "number")
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
    # Agrupar por sala para el template
    rooms_order = [Room.VIP, Room.TERRAZA, Room.PISO_1]
    room_labels = dict(Room.choices)
    rooms = []
    for code in rooms_order:
        rows = [r for r in table_rows if r["table"].room == code]
        rooms.append({"code": code, "label": room_labels[code], "rows": rows})

    return render(
        request,
        "reservations/floor_plan.html",
        {"tables": table_rows, "rooms": rooms},
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