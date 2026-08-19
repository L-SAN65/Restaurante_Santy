from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from core.models import BusinessConfig, Role

from .models import Dish, Order, OrderItem, OrderStatus, Shrinkage


def _guard_waiter(request):
    if request.user.role != Role.WAITER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return None


def _guard_chef(request):
    if request.user.role != Role.CHEF:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return None


def _totals(items):
    """Subtotal, IVA y total de una lista de ítems (RF-21)."""
    config = BusinessConfig.objects.get(pk=1)
    subtotal = sum((i.quantity * i.unit_price for i in items), Decimal("0"))
    subtotal = subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    vat_amount = (subtotal * config.vat_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    total = subtotal + vat_amount
    return subtotal, vat_amount, total


# ---------------------------------------------------------------------------
# Mesero: toma de comanda (RF-20) y segmentación de cuenta (RF-22)
# ---------------------------------------------------------------------------


@login_required
def order_create(request, table_id):
    """Crea una comanda: único activo por mesa, deduce insumos vía Ficha Técnica."""
    blocked = _guard_waiter(request)
    if blocked:
        return blocked

    from reservations.models import Table

    table = get_object_or_404(Table, pk=table_id, disabled=False)

    # Comanda activa de la mesa (si existe) para continuar la cuenta
    active_order = table.orders.filter(
        status__in=[OrderStatus.WAITING, OrderStatus.PREPARING, OrderStatus.READY]
    ).first()

    if request.method == "POST":
        dish_ids = request.POST.getlist("dish_id")
        quantities = request.POST.getlist("qty")
        notes = request.POST.getlist("notes")

        items = []
        for dish_id, qty_raw, note in zip(dish_ids, quantities, notes):
            if not dish_id:
                continue
            try:
                qty = int(qty_raw or 0)
            except (TypeError, ValueError):
                continue
            if qty <= 0:
                continue
            dish = Dish.objects.filter(pk=dish_id, active=True).first()
            if dish is None:
                continue
            items.append((dish, qty, note.strip() or ""))

        if not items:
            messages.error(request, "Agregue al menos un platillo con cantidad válida.")
            return redirect("kitchen:order_create", table_id=table.pk)

        with transaction.atomic():
            # Verifica stock según Ficha Técnica (RF-14)
            from inventory.models import TechnicalSheet

            for dish, qty, _note in items:
                sheet = TechnicalSheet.objects.filter(dish=dish).first()
                if sheet is None:
                    continue
                if not all(
                    item.ingredient.current_stock >= item.quantity * qty
                    for item in sheet.ingredients.all()
                ):
                    messages.error(
                        request,
                        f"Stock insuficiente para {dish.name}. Servicio rechazado.",
                    )
                    return redirect("kitchen:order_create", table_id=table.pk)

            order = active_order or Order.objects.create(
                table=table, waiter=request.user, status=OrderStatus.WAITING
            )
            for dish, qty, note in items:
                OrderItem.objects.create(
                    order=order,
                    name=dish.name,
                    quantity=qty,
                    unit_price=dish.price,
                    notes=note,
                )

            # Deducción de insumos por Ficha Técnica (RF-20)
            for dish, qty, _note in items:
                sheet = TechnicalSheet.objects.filter(dish=dish).first()
                if sheet is not None:
                    for item in sheet.ingredients.all():
                        item.ingredient.apply_receipt(-1 * item.quantity * qty, 0)

        from audit.models import ActionType, AuditLog, Result

        AuditLog.log(
            request.user,
            ActionType.RESERVATION,
            Result.SUCCESS,
            object_type="Order",
            object_id=order.pk,
            detail=f"Comanda en mesa {table.number} con {len(items)} platillo(s).",
        )
        messages.success(request, f"Comanda enviada a cocina (mesa {table.number}).")
        return redirect("reservations:floor_plan")

    dishes = Dish.objects.filter(active=True)
    return render(
        request,
        "kitchen/order_create.html",
        {"table": table, "dishes": dishes, "active_order": active_order},
    )


@login_required
def account_segmentation(request, order_id):
    """Segmentación de cuenta en grupos independientes (RF-22)."""
    blocked = _guard_waiter(request)
    if blocked:
        return blocked
    from audit.models import ActionType, AuditLog, Result

    order = get_object_or_404(
        Order, pk=order_id, status__in=[OrderStatus.WAITING, OrderStatus.PREPARING, OrderStatus.READY]
    )
    items = list(order.items.all())

    split = None
    if request.method == "POST":
        group_by_item = {int(pk): g for pk, g in request.POST.items() if pk.isdigit() and g}
        groups = {}
        for item in items:
            group = group_by_item.get(str(item.pk), "1")
            groups.setdefault(group, []).append(item)
        split = []
        for group, group_items in sorted(groups.items()):
            subtotal, vat_amount, total = _totals(group_items)
            split.append({
                "name": f"Grupo {group}",
                "items": group_items,
                "subtotal": subtotal,
                "vat_amount": vat_amount,
                "total": total,
            })
        AuditLog.log(
            request.user,
            ActionType.RESERVATION,
            Result.SUCCESS,
            object_type="Order",
            object_id=order.pk,
            detail=f"Segmentación en {len(split)} grupo(s).",
        )

    return render(
        request,
        "kitchen/account_segmentation.html",
        {"order": order, "items": items, "split": split},
    )


# ---------------------------------------------------------------------------
# KDS (RF-05, RF-06)
# ---------------------------------------------------------------------------


@login_required
def kds(request):
    """Pantalla KDS: comandas en espera/preparación con semáforo de tiempos."""
    blocked = _guard_chef(request)
    if blocked:
        return blocked

    tickets = (
        Order.objects.filter(status__in=[OrderStatus.WAITING, OrderStatus.PREPARING])
        .select_related("table", "waiter")
        .prefetch_related("items")
    )
    return render(request, "kitchen/kds.html", {"tickets": tickets})


@login_required
def order_start(request, order_id):
    """WAITING → PREPARING: inicia el reloj del semáforo (RF-05)."""
    blocked = _guard_chef(request)
    if blocked:
        return blocked
    order = get_object_or_404(Order, pk=order_id)
    if order.status != OrderStatus.WAITING:
        messages.error(request, "Solo las comandas en espera pueden iniciarse.")
        return redirect("kitchen:kds")
    order.start_preparation()
    messages.success(request, "Comanda en preparación.")
    return redirect("kitchen:kds")


@login_required
def order_ready(request, order_id):
    """PREPARING → READY: platillo listo para entrega."""
    blocked = _guard_chef(request)
    if blocked:
        return blocked
    order = get_object_or_404(Order, pk=order_id)
    if order.status != OrderStatus.PREPARING:
        messages.error(request, "Solo las comandas en preparación pueden marcarse listas.")
        return redirect("kitchen:kds")
    order.status = OrderStatus.READY
    order.save(update_fields=["status"])
    messages.success(request, "Comanda lista para entregar.")
    return redirect("kitchen:kds")


@login_required
def order_delivered(request, order_id):
    """READY → DELIVERED: la mesa queda disponible nuevamente (RF-20/31)."""
    blocked = _guard_chef(request)
    if blocked:
        return blocked
    from django.utils import timezone

    order = get_object_or_404(Order, pk=order_id)
    if order.status != OrderStatus.READY:
        messages.error(request, "Solo las comandas listas pueden entregarse.")
        return redirect("kitchen:kds")
    order.status = OrderStatus.DELIVERED
    order.completed_at = timezone.now()
    order.save(update_fields=["status", "completed_at"])
    messages.success(request, f"Comanda entregada en mesa {order.table.number}.")
    return redirect("kitchen:kds")


@login_required
def shrinkage(request, order_id):
    """Registra merma auditada con reposición a $0.00 (RF-06)."""
    blocked = _guard_chef(request)
    if blocked:
        return blocked
    from audit.models import ActionType, AuditLog, Result

    order = get_object_or_404(Order, pk=order_id)
    items = order.items.all()

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        reason = request.POST.get("reason", "").strip()
        notify = request.POST.get("notify_waiter_replacement") == "on"

        item = get_object_or_404(OrderItem, pk=item_id, order=order)
        if not reason:
            messages.error(request, "El motivo de la merma es obligatorio.")
            return redirect("kitchen:shrinkage", order_id=order.pk)

        if item.cancelled_reason:
            messages.error(request, "El ítem ya fue cancelado por merma.")
            return redirect("kitchen:shrinkage", order_id=order.pk)

        item.cancelled_reason = f"Merma: {reason}"
        item.save(update_fields=["cancelled_reason"])

        shrinkage = Shrinkage.objects.create(
            order_item=item,
            reason=reason,
            registered_by=request.user,
            notify_waiter_replacement=notify,
            replaced_amount=Decimal("0.00"),
        )
        AuditLog.log(
            request.user,
            ActionType.SHRINKAGE,
            Result.SUCCESS,
            object_type="OrderItem",
            object_id=item.pk,
            detail=f"Merma de {item.name} en mesa {order.table.number}: {reason}",
        )
        note = " Alerta de reposición a $0.00 enviada al Mesero." if notify else ""
        messages.success(request, f"Merma registrada: {item.name}.{note}")
        return redirect("kitchen:kds")

    return render(
        request,
        "kitchen/shrinkage.html",
        {"order": order, "items": items, "shrinkages": Shrinkage.objects.select_related("order_item").filter(order_item__order=order)},
    )