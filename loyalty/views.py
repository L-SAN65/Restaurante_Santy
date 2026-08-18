from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.models import Role

from .models import LoyaltyMovement


def _guard_cashier(request):
    if request.user.role != Role.CASHIER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return None


@login_required
def wallet_view(request):
    """Historial y saldo de puntos por cédula (RF-15..17, CP-17..19)."""
    blocked = _guard_cashier(request)
    if blocked:
        return blocked

    cedula = request.GET.get("cedula", "").strip()

    context = {
        "cedula": cedula,
        "balance": 0,
        "movements": [],
        "searched": False,
    }
    if cedula:
        context["balance"] = LoyaltyMovement.balance(cedula)
        context["movements"] = LoyaltyMovement.objects.filter(
            client_cedula=cedula
        )[:50]
        context["searched"] = True

    return render(request, "loyalty/wallet.html", context)


@login_required
def redeem_view(request):
    """Canje de puntos vigentes: 10 pts = $1 de descuento (RF-16)."""
    blocked = _guard_cashier(request)
    if blocked:
        return blocked

    if request.method == "POST":
        cedula = request.POST.get("cedula", "").strip()
        points_raw = request.POST.get("points", "").strip()
        subtotal_raw = request.POST.get("subtotal", "").strip()

        try:
            points = int(points_raw)
            subtotal = float(subtotal_raw)
        except (TypeError, ValueError):
            messages.error(request, "Ingrese un número de puntos y un subtotal válidos.")
            return redirect("loyalty:wallet")

        try:
            discount = LoyaltyMovement.redeem(cedula, points, subtotal)
            messages.success(
                request,
                f"Canje exitoso: {points} puntos → ${discount:.2f} de descuento.",
            )
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect("loyalty:wallet")

    return redirect("loyalty:wallet")