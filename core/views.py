from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import redirect, render

from audit.models import ActionType, AuditLog, Result

from .models import Role, User


def _resolve_user(identifier):
    try:
        return User.objects.get(username__iexact=identifier)
    except User.DoesNotExist:
        return None


def login_view(request):
    """Login exclusivo del personal (ADMIN, CASHIER, WAITER, CHEF, WAREHOUSE).

    Los clientes deben usar /reservas/login/ (reservations:client_login).
    Este formulario rechaza Role.CLIENT para mantener los flujos separados.
    """
    if request.user.is_authenticated:
        # Si es cliente, mandarlo a su portal; si es staff, a su dashboard
        if request.user.role == Role.CLIENT:
            return redirect("reservations:portal")
        return redirect(request.user.dashboard_url)

    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = _resolve_user(identifier)
        if user is None:
            AuditLog.log(None, ActionType.LOGIN_FAILED, Result.FAILURE,
                         object_type="USER", detail=f"Email no registrado: {identifier}")
            messages.error(request, "Credenciales inválidas.")
            return render(request, "core/staff_login.html")

        # Separación de formularios: este endpoint es solo personal
        if user.role == Role.CLIENT:
            AuditLog.log(user, ActionType.LOGIN_FAILED, Result.FAILURE,
                         object_type="USER", object_id=user.pk, detail="Intento de login staff con cuenta CLIENT")
            messages.error(request, "Esta cuenta es de cliente. Use el acceso de clientes en /reservas/login/.")
            return render(request, "core/staff_login.html")

        allowed, reason = user.login_allowed()
        if not allowed:
            AuditLog.log(user, ActionType.LOGIN_FAILED, Result.FAILURE,
                         object_type="USER", object_id=user.pk, detail=reason)
            messages.error(request, reason)
            return render(request, "core/staff_login.html")

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
        return render(request, "core/staff_login.html")

    return render(request, "core/staff_login.html")


def client_register_view(request):
    """Registro de cliente (Luxe Dining) — crea usuario CLIENT y loguea automáticamente."""
    if request.user.is_authenticated:
        if request.user.role == Role.CLIENT:
            return redirect("reservations:portal")
        return redirect(request.user.dashboard_url)

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        cedula = request.POST.get("cedula", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        # Validaciones básicas
        if not full_name or not cedula or not email or not password:
            messages.error(request, "Complete todos los campos obligatorios.")
            return render(request, "reservations/register.html")

        if password != confirm:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "reservations/register.html")

        if len(password) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return render(request, "reservations/register.html")

        if User.objects.filter(username__iexact=email).exists():
            messages.error(request, "Ya existe una cuenta con ese correo.")
            return render(request, "reservations/register.html")

        if cedula and User.objects.filter(cedula=cedula).exists():
            messages.error(request, "Ya existe una cuenta con esa cédula.")
            return render(request, "reservations/register.html")

        # Split name
        parts = full_name.split()
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            cedula=cedula,
            role=Role.CLIENT,
        )
        AuditLog.log(user, ActionType.LOGIN, Result.SUCCESS,
                     object_type="USER", object_id=user.pk, detail=f"Registro cliente {email} tel:{phone}")
        auth_user = authenticate(request, username=email, password=password)
        if auth_user:
            auth_login(request, auth_user)
        messages.success(request, "Cuenta creada. ¡Bienvenido a Luxe Dining!")
        next_url = request.GET.get("next") or request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("reservations:portal")

    return render(request, "reservations/register.html")


def client_login_view(request):
    """Login para clientes (Role.CLIENT) — Luxe Dining, respeta ?next=."""
    if request.user.is_authenticated:
        if request.user.role == Role.CLIENT:
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("reservations:portal")
        return redirect(request.user.dashboard_url)

    next_url = request.GET.get("next") or request.POST.get("next") or ""

    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = _resolve_user(identifier)
        if user is None:
            AuditLog.log(None, ActionType.LOGIN_FAILED, Result.FAILURE,
                         object_type="USER", detail=f"Email no registrado: {identifier}")
            messages.error(request, "Credenciales inválidas.")
            return render(request, "reservations/login.html", {"next": next_url})

        if user.role != Role.CLIENT:
            AuditLog.log(user, ActionType.LOGIN_FAILED, Result.FAILURE,
                         object_type="USER", object_id=user.pk, detail="Intento de login cliente con cuenta staff")
            messages.error(request, "Esta área es solo para clientes.")
            return render(request, "reservations/login.html", {"next": next_url})

        allowed, reason = user.login_allowed()
        if not allowed:
            AuditLog.log(user, ActionType.LOGIN_FAILED, Result.FAILURE,
                         object_type="USER", object_id=user.pk, detail=reason)
            messages.error(request, reason)
            return render(request, "reservations/login.html", {"next": next_url})

        auth_user = authenticate(request, username=user.username, password=password)
        if auth_user is not None:
            auth_user.reset_login_attempts()
            auth_login(request, auth_user)
            AuditLog.log(auth_user, ActionType.LOGIN, Result.SUCCESS,
                         object_type="USER", object_id=auth_user.pk)
            if next_url:
                return redirect(next_url)
            return redirect("reservations:portal")

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
        return render(request, "reservations/login.html", {"next": next_url})

    return render(request, "reservations/login.html", {"next": next_url})


class CustomLogoutView(View):
    """Logout con redirección según rol (evita `registration/logged_out.html` de Django):

    - CLIENT (personal) → menú público (`reservations:menu`)
    - Staff/empresa (ADMIN, CASHIER, WAITER, CHEF, WAREHOUSE) → login del personal (`core:login`)
    Respeta `?next=` / `next` POST si se envía explícitamente.
    Acepta GET y POST (útil si el navegador hace GET al /logout/).
    """

    def _do_logout(self, request):
        role = None
        if request.user.is_authenticated:
            role = request.user.role
            AuditLog.log(request.user, ActionType.LOGOUT, Result.SUCCESS,
                         object_type="USER", object_id=request.user.pk)
            auth_logout(request)
        else:
            # Aunque no esté autenticado, limpiar sesión por seguridad
            auth_logout(request)
        explicit = request.POST.get("next") or request.GET.get("next")
        if explicit:
            return redirect(explicit)
        if role == Role.CLIENT:
            return redirect("reservations:menu")
        return redirect("core:login")

    def get(self, request, *args, **kwargs):
        return self._do_logout(request)

    def post(self, request, *args, **kwargs):
        return self._do_logout(request)


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


def _guard_admin(request):
    if request.user.role != Role.ADMIN:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return None


@login_required
def user_management(request):
    """Gestión de roles y usuarios — solo ADMIN (RF-01).

    Lista usuarios, permite cambiar rol, desbloquear cuentas (reset de fallos)
    y crear usuarios de personal. Auditoría de cada cambio.
    """
    blocked = _guard_admin(request)
    if blocked:
        return blocked

    from audit.models import ActionType, AuditLog, Result

    if request.method == "POST":
        action = request.POST.get("action")
        user_id = request.POST.get("user_id")
        target = None
        if user_id:
            from django.shortcuts import get_object_or_404
            target = get_object_or_404(User, pk=user_id)

        if action == "change_role" and target:
            new_role = request.POST.get("role", "").strip()
            valid_roles = [c[0] for c in Role.choices]
            if new_role not in valid_roles:
                messages.error(request, "Rol no válido.")
                return redirect("core:user_management")
            if target == request.user and new_role != Role.ADMIN:
                messages.error(request, "No puede quitarse su propio rol de Administrador.")
                return redirect("core:user_management")
            old_role = target.role
            target.role = new_role
            target.save(update_fields=["role"])
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="User", object_id=target.pk,
                         detail=f"Cambio de rol {old_role} → {new_role} para {target.email}")
            messages.success(request, f"Rol de {target.email} cambiado a {target.get_role_display()}.")
            return redirect("core:user_management")

        if action == "unlock" and target:
            target.reset_login_attempts()
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="User", object_id=target.pk,
                         detail=f"Desbloqueo de cuenta {target.email}")
            messages.success(request, f"Cuenta {target.email} desbloqueada.")
            return redirect("core:user_management")

        if action == "change_password" and target:
            # Solo ADMIN puede cambiar clave del personal (no CLIENT)
            if target.role == Role.CLIENT:
                messages.error(request, "Las claves de clientes no se cambian aquí. El cliente usa recuperación propia.")
                return redirect("core:user_management")
            new_password = request.POST.get("new_password", "").strip()
            if len(new_password) < 8:
                messages.error(request, "La nueva contraseña debe tener al menos 8 caracteres.")
                return redirect("core:user_management")
            target.set_password(new_password)
            target.save(update_fields=["password"])
            # Desbloquear por si estaba suspendida
            try:
                target.reset_login_attempts()
            except Exception:
                pass
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="User", object_id=target.pk,
                         detail=f"Cambio de clave por ADMIN para {target.email} ({target.get_role_display()})")
            messages.success(request, f"Contraseña de {target.email} actualizada. El usuario debe usar la nueva clave en el próximo inicio de sesión.")
            return redirect("core:user_management")

        if action == "create":
            email = request.POST.get("email", "").strip().lower()
            cedula = request.POST.get("cedula", "").strip()
            role = request.POST.get("role", "").strip()
            password = request.POST.get("password", "").strip()
            first_name = request.POST.get("first_name", "").strip()
            if not email or not role or not password:
                messages.error(request, "Email, rol y contraseña son obligatorios.")
                return redirect("core:user_management")
            if User.objects.filter(username__iexact=email).exists():
                messages.error(request, "Ya existe un usuario con ese email.")
                return redirect("core:user_management")
            if cedula and User.objects.filter(cedula=cedula).exists():
                messages.error(request, "Ya existe un usuario con esa cédula.")
                return redirect("core:user_management")
            valid_roles = [c[0] for c in Role.choices]
            if role not in valid_roles:
                messages.error(request, "Rol no válido.")
                return redirect("core:user_management")
            user = User.objects.create_user(
                username=email, email=email, password=password,
                first_name=first_name, cedula=cedula or None, role=role,
                is_staff=(role == Role.ADMIN),
            )
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="User", object_id=user.pk,
                         detail=f"Creación de usuario {email} rol {role}")
            messages.success(request, f"Usuario {email} creado como {user.get_role_display()}.")
            return redirect("core:user_management")

        messages.error(request, "Acción no reconocida.")
        return redirect("core:user_management")

    users = User.objects.all().order_by("role", "username")
    return render(request, "core/user_management.html", {"users": users, "roles": Role.choices})


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