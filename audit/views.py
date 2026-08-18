import secrets
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from core.models import BusinessConfig, Role

from .models import ActionType, AuditLog, PinToken, Result


@login_required
def audit_trail(request):
    blocked = _guard_admin(request)
    if blocked:
        return blocked
    entries = AuditLog.objects.select_related("user")[:200]
    return render(request, "audit/trail.html", {"entries": entries})


def _guard_admin(request):
    if request.user.role != Role.ADMIN:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return None


@login_required
def pin_generate(request):
    """Genera un PIN temporal de un solo uso, vigente 60 s (RF-18)."""
    blocked = _guard_admin(request)
    if blocked:
        return blocked

    if request.method == "POST":
        action = request.POST.get("action", "").strip() or "Operación sensible"
        config = BusinessConfig.objects.get(pk=1)

        code = f"{secrets.randbelow(1000000):06d}"
        token = PinToken.objects.create(
            code=code,
            issued_by=request.user,
            valid_until=timezone.now() + timedelta(seconds=config.pin_ttl_seconds),
            action=action,
        )
        AuditLog.log(
            request.user,
            ActionType.PIN_ISSUE,
            Result.SUCCESS,
            object_type="PINToken",
            object_id=token.pk,
            detail=action,
        )
        messages.success(request, f"PIN generado: {code} · vigente 60 segundos · un solo uso.")
        return redirect("audit:pin")

    return render(request, "audit/pin.html", {"ttl_seconds": 60})


@login_required
def pin_validate(request):
    """Valida un PIN dentro de los 60 s; lo invalida al consumirse (RF-19)."""
    blocked = _guard_admin(request)
    if blocked:
        return blocked

    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        token = PinToken.objects.filter(code=code).order_by("-issued_at").first()

        if token is None:
            messages.error(request, "PIN no encontrado.")
            AuditLog.log(request.user, ActionType.PIN_CONSUMED, Result.FAILURE,
                         object_type="PINToken", detail=f"PIN inexistente: {code}")
            return redirect("audit:pin")

        if not token.is_valid:
            messages.error(request, "PIN expirado o ya consumido.")
            AuditLog.log(request.user, ActionType.PIN_CONSUMED, Result.FAILURE,
                         object_type="PINToken", object_id=token.pk,
                         detail="Expirado o consumido")
            return redirect("audit:pin")

        token.consumed_at = timezone.now()
        token.save(update_fields=["consumed_at"])
        AuditLog.log(request.user, ActionType.PIN_CONSUMED, Result.SUCCESS,
                     object_type="PINToken", object_id=token.pk,
                     detail=f"Autorizado: {token.action}")
        messages.success(request, f"PIN válido. Operación autorizada: {token.action}")
        return redirect("audit:pin")

    return render(request, "audit/pin.html", {"ttl_seconds": 60})