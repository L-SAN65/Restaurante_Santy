from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, render

from audit.models import ActionType, AuditLog, Result

from .models import Role, User


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


def client_login_view(request):
    """Login para clientes (Role.CLIENT) — redirige a mis reservas."""
    if request.user.is_authenticated:
        if request.user.role == Role.CLIENT:
            return redirect("reservations:my_reservations")
        return redirect(request.user.dashboard_url)

    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = _resolve_user(identifier)
        if user is None:
            AuditLog.log(None, ActionType.LOGIN_FAILED, Result.FAILURE,
                         object_type="USER", detail=f"Email no registrado: {identifier}")
            messages.error(request, "Credenciales inválidas.")
            return render(request, "reservations/login.html")

        if user.role != Role.CLIENT:
            AuditLog.log(user, ActionType.LOGIN_FAILED, Result.FAILURE,
                         object_type="USER", object_id=user.pk, detail="Intento de login cliente con cuenta staff")
            messages.error(request, "Esta área es solo para clientes.")
            return render(request, "reservations/login.html")

        allowed, reason = user.login_allowed()
        if not allowed:
            AuditLog.log(user, ActionType.LOGIN_FAILED, Result.FAILURE,
                         object_type="USER", object_id=user.pk, detail=reason)
            messages.error(request, reason)
            return render(request, "reservations/login.html")

        auth_user = authenticate(request, username=user.username, password=password)
        if auth_user is not None:
            auth_user.reset_login_attempts()
            auth_login(request, auth_user)
            AuditLog.log(auth_user, ActionType.LOGIN, Result.SUCCESS,
                         object_type="USER", object_id=auth_user.pk)
            return redirect("reservations:my_reservations")

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
        return render(request, "reservations/login.html")

    return render(request, "reservations/login.html")


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


@login_required
def admin_dashboard(request):
    if not request.user.role == Role.ADMIN:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    from django.db.models import Sum
    from django.utils import timezone
    from billing.models import Invoice
    from kitchen.models import Order
    from inventory.models import Ingredient
    from reservations.models import Table, TableStatus

    today = timezone.localdate()
    context = {
        "today_total": Invoice.objects.filter(issued_at__date=today).aggregate(
            total=Sum("total")
        )["total"]
        or 0,
        "active_orders": Order.objects.exclude(status__in=["CANCELLED", "DELIVERED"]).count(),
        "low_stock": sum(
            1 for i in Ingredient.objects.filter(active=True) if i.current_stock < i.min_stock
        ),
        "occupied_tables": sum(
            1 for t in Table.objects.all() if t.status == TableStatus.OCCUPIED
        ),
        "table_count": Table.objects.count(),
    }
    return render(request, "core/admin_dashboard.html", context)


@login_required
def cashier_dashboard(request):
    if not request.user.role == Role.CASHIER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    from django.db.models import Sum
    from django.utils import timezone
    from billing.models import CashRegister, CashRegisterStatus, Invoice, InvoiceStatus
    from loyalty.models import LoyaltyMovement, MovementType

    today = timezone.localdate()
    invoices = Invoice.objects.filter(issued_at__date=today)
    context = {
        "today_total": invoices.aggregate(total=Sum("total"))["total"] or 0,
        "today_invoices": invoices.count(),
        "active_register": CashRegister.objects.filter(
            status=CashRegisterStatus.OPEN
        ).first(),
        "open_invoices": Invoice.objects.filter(status=InvoiceStatus.DRAFT).count(),
        "redeemed_points": LoyaltyMovement.objects.filter(
            movement_type=MovementType.REDEMPTION, created_at__date=today
        ).count(),
    }
    return render(request, "core/cashier_dashboard.html", context)


@login_required
def waiter_dashboard(request):
    if not request.user.role == Role.WAITER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    from reservations.models import Table, TableStatus

    tables = list(Table.objects.all())
    counts = {TableStatus.AVAILABLE: 0, TableStatus.OCCUPIED: 0, TableStatus.RESERVED: 0, TableStatus.BLOCKED: 0}
    for table in tables:
        counts[table.status] = counts.get(table.status, 0) + 1
    return render(
        request,
        "core/waiter_dashboard.html",
        {
            "tables": tables,
            "counts": {
                "available": counts[TableStatus.AVAILABLE],
                "occupied": counts[TableStatus.OCCUPIED],
                "reserved": counts[TableStatus.RESERVED],
                "blocked": counts[TableStatus.BLOCKED],
            },
        },
    )


@login_required
def chef_dashboard(request):
    if not request.user.role == Role.CHEF:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    from kitchen.models import Order, OrderStatus, Shrinkage
    from django.utils import timezone

    orders = Order.objects.select_related("table")
    preparing = orders.filter(status=OrderStatus.PREPARING)
    context = {
        "preparing_count": preparing.count(),
        "waiting_count": orders.filter(status=OrderStatus.WAITING).count(),
        "overdue_count": sum(
            1 for o in preparing if o.traffic_light == "red"
        ),
        "shrinkage_count": Shrinkage.objects.filter(
            registered_at__date=timezone.localdate()
        ).count(),
        "recent_orders": orders[:10],
    }
    return render(request, "core/chef_dashboard.html", context)


@login_required
def warehouse_dashboard(request):
    if not request.user.role == Role.WAREHOUSE:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    from inventory.models import Ingredient, TechnicalSheet

    ingredients = Ingredient.objects.all()
    critical = [
        ing for ing in ingredients if ing.current_stock < ing.min_stock
    ]
    totals = {
        "total_ingredients": ingredients.count(),
        "critical": len(critical),
        "sheets": TechnicalSheet.objects.count(),
        "total_value": sum(ing.current_stock * ing.average_cost for ing in ingredients),
    }
    return render(
        request,
        "core/warehouse_dashboard.html",
        {"totals": totals, "inventory_items": critical[:20]},
    )