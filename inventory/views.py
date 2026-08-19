from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.models import Role

from .models import (
    CorrectionRequest,
    CorrectionRequestStatus,
    Ingredient,
    Receipt,
    TechnicalSheet,
)


def _guard_warehouse(request):
    if request.user.role != Role.WAREHOUSE:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return None


def _guard_admin(request):
    if request.user.role != Role.ADMIN:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return None


@login_required
def dashboard(request):
    """Dashboard de inventario con datos reales de insumos, stock y valor."""
    blocked = _guard_warehouse(request)
    if blocked:
        return blocked

    ingredients = Ingredient.objects.filter(active=True)
    total_value = sum(i.current_stock * i.average_cost for i in ingredients)
    critical = [i for i in ingredients if i.below_minimum]
    sheets = TechnicalSheet.objects.select_related("dish")

    hy_history = []
    for receipt in Receipt.objects.select_related("ingredient", "received_by")[:10]:
        hy_history.append({
            "type": "Recepción",
            "description": f"{receipt.ingredient.name} × {receipt.quantity} {receipt.ingredient.unit}",
            "formatted_date": receipt.created_at.strftime("%d/%m/%Y %H:%M"),
        })

    return render(
        request,
        "inventory/dashboard.html",
        {
            "totals": {
                "total_value": total_value,
                "total_ingredients": ingredients.count(),
                "critical": len(critical),
                "sheets": sheets.count(),
            },
            "critical_ingredients": critical[:12],
            "history": hy_history,
            "ingredients": ingredients[:40],
        },
    )


# ---------------------------------------------------------------------------
# Recepciones (RF-23)
# ---------------------------------------------------------------------------


@login_required
def receipts(request):
    """Lista y registra recepciones de lotes con costo y caducidad."""
    blocked = _guard_warehouse(request)
    if blocked:
        return blocked
    from decimal import Decimal

    if request.method == "POST":
        ingredient_id = request.POST.get("ingredient")
        qty_raw = request.POST.get("quantity", "").strip()
        cost_raw = request.POST.get("unit_cost", "").strip()
        lot = request.POST.get("lot", "").strip()
        expiry_raw = request.POST.get("expiry_date", "").strip()

        ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
        try:
            quantity = Decimal(qty_raw)
            unit_cost = Decimal(cost_raw)
            if quantity <= 0 or unit_cost < 0:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, "Ingrese cantidad y costo válidos.")
            return redirect("inventory:receipts")

        expire_date = None
        if expiry_raw:
            try:
                from datetime import datetime
                expire_date = datetime.strptime(expiry_raw, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Fecha de caducidad inválida.")
                return redirect("inventory:receipts")

        Receipt.objects.create(
            ingredient=ingredient,
            received_by=request.user,
            quantity=quantity,
            unit_cost=unit_cost,
            lot=lot,
            expiry_date=expire_date,
            confirmed=False,
        )
        messages.success(
            request,
            f"Recepción creada para {ingredient.name} × {quantity} {ingredient.unit}. "
            "Confirme la recepción para aplicar stock.",
        )
        return redirect("inventory:receipts")

    return render(
        request,
        "inventory/receipts.html",
        {
            "ingredients": Ingredient.objects.filter(active=True),
            "receipts": Receipt.objects.select_related("ingredient", "received_by"),
        },
    )


@login_required
def receipt_confirm(request, receipt_id):
    """Confirma la recepción: aplica stock y recalcula costo promedio (RF-23)."""
    blocked = _guard_warehouse(request)
    if blocked:
        return blocked
    from audit.models import ActionType, AuditLog, Result

    receipt = get_object_or_404(Receipt, pk=receipt_id)
    try:
        receipt.confirm()
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("inventory:receipts")

    AuditLog.log(
        request.user,
        ActionType.INVENTORY_CORRECTION,
        Result.SUCCESS,
        object_type="Receipt",
        object_id=receipt.pk,
        detail=(
            f"Recepción {receipt.pk} confirmada: {receipt.ingredient.name} × "
            f"{receipt.quantity} {receipt.ingredient.unit} a ${receipt.unit_cost}."
        ),
    )
    messages.success(
        request,
        f"Recepción confirmada. Stock y costo promedio de {receipt.ingredient.name} actualizados.",
    )
    return redirect("inventory:receipts")


# ---------------------------------------------------------------------------
# Correcciones de recepciones confirmadas (RF-24)
# ---------------------------------------------------------------------------


@login_required
def corrections(request):
    """Solicitudes de corrección de recepciones confirmadas."""
    blocked = _guard_warehouse(request)
    if blocked:
        return blocked
    from decimal import Decimal

    if request.method == "POST":
        receipt_id = request.POST.get("receipt")
        diff_raw = request.POST.get("difference_quantity", "").strip()
        reason = request.POST.get("reason", "").strip()

        receipt = get_object_or_404(Receipt, pk=receipt_id)
        if not receipt.confirmed:
            messages.error(request, "Solo se corrigen recepciones confirmadas.")
            return redirect("inventory:corrections")
        try:
            difference = Decimal(diff_raw)
        except (TypeError, ValueError):
            messages.error(request, "Ingrese una diferencia de cantidad válida.")
            return redirect("inventory:corrections")
        if not reason:
            messages.error(request, "La justificación es obligatoria.")
            return redirect("inventory:corrections")

        CorrectionRequest.objects.create(
            receipt=receipt,
            requested_by=request.user,
            difference_quantity=difference,
            reason=reason,
        )
        messages.success(
            request,
            "Solicitud de corrección creada (Pendiente de Aprobación).",
        )
        return redirect("inventory:corrections")

    return render(
        request,
        "inventory/corrections.html",
        {
            "confirmed_receipts": Receipt.objects.filter(confirmed=True).select_related("ingredient"),
            "requests": CorrectionRequest.objects.select_related(
                "receipt__ingredient", "requested_by", "reviewed_by"
            ),
        },
    )


@login_required
def correction_review(request, correction_id):
    """Aprueba o rechaza la corrección (Administrador), auditable (RF-24)."""
    if request.user.role not in (Role.ADMIN,):
        messages.error(request, "Solo el Administrador puede revisar correcciones.")
        return redirect(request.user.dashboard_url)
    from audit.models import ActionType, AuditLog, Result

    correction = get_object_or_404(CorrectionRequest, pk=correction_id)
    action = request.POST.get("action")

    try:
        if action == "approve":
            correction.approve(request.user)
            # Aplica la diferencia al stock de forma controlada
            receipt = correction.receipt
            receipt.ingredient.apply_receipt(correction.difference_quantity, 0)
        elif action == "reject":
            correction.reject(request.user)
        else:
            messages.error(request, "Acción inválida.")
            return redirect("inventory:corrections")
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("inventory:corrections")

    AuditLog.log(
        request.user,
        ActionType.INVENTORY_CORRECTION,
        Result.SUCCESS,
        object_type="CorrectionRequest",
        object_id=correction.pk,
        detail=f"Corrección de recepción {correction.receipt.pk} {action}d.",
    )
    messages.success(request, f"Corrección {action}da. Registrada en auditoría.")
    return redirect("inventory:corrections")