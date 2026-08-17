from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, render

from audit.models import ActionType, AuditLog, Result

from .models import Role, User


def _denied_templates():
    return {
        Role.ADMIN: "core/admin_dashboard.html",
        Role.CASHIER: "core/cashier_dashboard.html",
        Role.WAITER: "core/waiter_dashboard.html",
        Role.CHEF: "core/chef_dashboard.html",
        Role.WAREHOUSE: "core/warehouse_dashboard.html",
        Role.CLIENT: "reservations/portal.html",
    }


def _resolve_user(identifier):
    try:
        return User.objects.get(username__iexact=identifier)
    except User.DoesNotExist:
        return None


def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.dashboard_url)

    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = _resolve_user(identifier)
        if user is None:
            AuditLog.log(None, ActionType.LOGIN_FAILED, Result.FAILURE,
                         object_type="USER", detail=f"Email no registrado: {identifier}")
            messages.error(request, "Credenciales inválidas.")
            return render(request, "core/login.html")

        allowed, reason = user.login_allowed()
        if not allowed:
            AuditLog.log(user, ActionType.LOGIN_FAILED, Result.FAILURE,
                         object_type="USER", object_id=user.pk, detail=reason)
            messages.error(request, reason)
            return render(request, "core/login.html")

        auth_user = authenticate(request, username=user.username, password=password)
        if auth_user is not None:
            auth_user.reset_login_attempts()
            auth_login(request, auth_user)
            AuditLog.log(auth_user, ActionType.LOGIN, Result.SUCCESS,
                         object_type="USER", object_id=auth_user.pk)
            return redirect(auth_user.dashboard_url)

        user.record_failed_login()
        AuditLog.log(user, ActionType.LOGIN_FAILED, Result.FAILURE,
                     object_type="USER", object_id=user.pk,
                     detail=f"Fallos consecutivos: {user.failed_login_count}")
        if user.is_permanently_locked:
            messages.error(request, "Cuenta bloqueada. Contacte al administrador.")
        elif user.suspended_until:
            messages.error(request, "Cuenta suspendida por 15 minutos por intentos fallidos.")
        else:
            messages.error(request, "Credenciales inválidas.")
        return render(request, "core/login.html")

    return render(request, "core/login.html")


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            AuditLog.log(request.user, ActionType.LOGOUT, Result.SUCCESS,
                         object_type="USER", object_id=request.user.pk)
        return super().dispatch(request, *args, **kwargs)


@login_required
def dashboard(request):
    if request.user.role == Role.ADMIN:
        return redirect("core:admin_dashboard")
    if request.user.role == Role.CASHIER:
        return redirect("core:cashier_dashboard")
    if request.user.role == Role.WAITER:
        return redirect("core:waiter_dashboard")
    if request.user.role == Role.CHEF:
        return redirect("core:chef_dashboard")
    if request.user.role == Role.WAREHOUSE:
        return redirect("core:warehouse_dashboard")
    return redirect("reservations:portal")


def _render_dashboard(request, template):
    context = {
        "now_utc5": None,
    }
    return render(request, template, context)


@login_required
def admin_dashboard(request):
    if not request.user.role == Role.ADMIN:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return _render_dashboard(request, "core/admin_dashboard.html")


@login_required
def cashier_dashboard(request):
    if not request.user.role == Role.CASHIER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return _render_dashboard(request, "core/cashier_dashboard.html")


@login_required
def waiter_dashboard(request):
    if not request.user.role == Role.WAITER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return _render_dashboard(request, "core/waiter_dashboard.html")


@login_required
def chef_dashboard(request):
    if not request.user.role == Role.CHEF:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return _render_dashboard(request, "core/chef_dashboard.html")


@login_required
def warehouse_dashboard(request):
    if not request.user.role == Role.WAREHOUSE:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return _render_dashboard(request, "core/warehouse_dashboard.html")