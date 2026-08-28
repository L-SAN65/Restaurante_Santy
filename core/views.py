from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render

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


# ---------------------------------------------------------------------------
# Panel Administrador — Gestión integrada (RF-13/14/20/27)
# Platos, Mesas con ubicación y Insumos+Recetas dentro del dashboard ADMIN
# ---------------------------------------------------------------------------


@login_required
def admin_dishes(request):
    """Gestión de platos (Dish) — solo ADMIN. CRUD completo desde el dashboard."""
    blocked = _guard_admin(request)
    if blocked:
        return blocked
    from audit.models import ActionType, AuditLog, Result
    from kitchen.models import Dish
    from decimal import Decimal, InvalidOperation

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        if action == "create":
            name = request.POST.get("name", "").strip()
            price_raw = request.POST.get("price", "").strip()
            description = request.POST.get("description", "").strip()
            active = request.POST.get("active") == "on"
            image = request.FILES.get("image")
            if not name:
                messages.error(request, "El nombre del platillo es obligatorio.")
                return redirect("core:admin_dishes")
            try:
                price = Decimal(price_raw)
                if price < 0:
                    raise ValueError
            except (InvalidOperation, ValueError, TypeError):
                messages.error(request, "Precio inválido. Use formato 0.00 USD.")
                return redirect("core:admin_dishes")
            if Dish.objects.filter(name__iexact=name).exists():
                messages.error(request, f"Ya existe un platillo con el nombre «{name}».")
                return redirect("core:admin_dishes")
            # Validar imagen
            if image:
                if image.size > 2 * 1024 * 1024:
                    messages.error(request, "La imagen no debe superar 2MB.")
                    return redirect("core:admin_dishes")
                if not (image.content_type or "").startswith("image/"):
                    messages.error(request, "El archivo debe ser una imagen (JPG/PNG).")
                    return redirect("core:admin_dishes")
            try:
                dish = Dish.objects.create(name=name, price=price, description=description, active=active, image=image)
            except Exception as e:
                # En Vercel el FS es read-only fuera de /tmp; en local puede ser Pillow no instalado
                messages.error(request, f"Error al guardar la imagen: {e}. Verifique que Pillow esté instalado y que MEDIA_ROOT sea escribible.")
                return redirect("core:admin_dishes")
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="Dish", object_id=dish.pk, detail=f"Platillo creado: {name} ${price} img={bool(image)}")
            messages.success(request, f"Platillo «{name}» creado.")
            return redirect("core:admin_dishes")

        if action == "update":
            dish_id = request.POST.get("dish_id")
            dish = get_object_or_404(Dish, pk=dish_id) if dish_id else None
            if not dish:
                messages.error(request, "Platillo no encontrado.")
                return redirect("core:admin_dishes")
            name = request.POST.get("name", "").strip()
            price_raw = request.POST.get("price", "").strip()
            description = request.POST.get("description", "").strip()
            active = request.POST.get("active") == "on"
            image = request.FILES.get("image")
            remove_image = request.POST.get("remove_image") == "on"
            if not name:
                messages.error(request, "El nombre es obligatorio.")
                return redirect("core:admin_dishes")
            try:
                price = Decimal(price_raw)
                if price < 0:
                    raise ValueError
            except (InvalidOperation, ValueError, TypeError):
                messages.error(request, "Precio inválido.")
                return redirect("core:admin_dishes")
            if Dish.objects.filter(name__iexact=name).exclude(pk=dish.pk).exists():
                messages.error(request, f"Ya existe otro platillo con el nombre «{name}».")
                return redirect("core:admin_dishes")
            dish.name = name
            dish.price = price
            dish.description = description
            dish.active = active
            if remove_image and dish.image:
                dish.image.delete(save=False)
                dish.image = None
            if image:
                if image.size > 2 * 1024 * 1024:
                    messages.error(request, "La imagen no debe superar 2MB.")
                    return redirect("core:admin_dishes")
                if not (image.content_type or "").startswith("image/"):
                    messages.error(request, "El archivo debe ser una imagen.")
                    return redirect("core:admin_dishes")
                if dish.image:
                    try:
                        dish.image.delete(save=False)
                    except Exception:
                        pass
                dish.image = image
            try:
                dish.save()
            except Exception as e:
                messages.error(request, f"Error al guardar la imagen: {e}.")
                return redirect("core:admin_dishes")
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="Dish", object_id=dish.pk, detail=f"Platillo actualizado: {name} ${price} activo={active} img={bool(dish.image)}")
            messages.success(request, f"Platillo «{name}» actualizado.")
            return redirect("core:admin_dishes")

        if action == "toggle":
            dish_id = request.POST.get("dish_id")
            dish = get_object_or_404(Dish, pk=dish_id)
            dish.active = not dish.active
            dish.save(update_fields=["active"])
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="Dish", object_id=dish.pk, detail=f"Platillo {'activado' if dish.active else 'desactivado'}: {dish.name}")
            messages.success(request, f"Platillo «{dish.name}» {'activado' if dish.active else 'desactivado'}.")
            return redirect("core:admin_dishes")

        if action == "delete":
            dish_id = request.POST.get("dish_id")
            dish = get_object_or_404(Dish, pk=dish_id)
            name = dish.name
            # Si tiene ficha técnica, eliminarla en cascada evita órfanos
            if dish.image:
                try:
                    dish.image.delete(save=False)
                except Exception:
                    pass
            dish.delete()
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="Dish", object_id="", detail=f"Platillo eliminado: {name}")
            messages.success(request, f"Platillo «{name}» eliminado.")
            return redirect("core:admin_dishes")

        messages.error(request, "Acción no reconocida.")
        return redirect("core:admin_dishes")

    from kitchen.models import Dish
    dishes = Dish.objects.all().order_by("name")
    # Conteo de fichas para indicador
    from inventory.models import TechnicalSheet
    sheets_by_dish = set(TechnicalSheet.objects.values_list("dish_id", flat=True))
    return render(request, "core/admin_dishes.html", {
        "dishes": dishes,
        "sheets_by_dish": sheets_by_dish,
    })


@login_required
def admin_tables(request):
    """Gestión de mesas con ubicación (x,y, forma) — solo ADMIN."""
    blocked = _guard_admin(request)
    if blocked:
        return blocked
    from audit.models import ActionType, AuditLog, Result
    from reservations.models import Table

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        if action == "create":
            number_raw = request.POST.get("number", "").strip()
            capacity_raw = request.POST.get("capacity", "").strip()
            x_raw = request.POST.get("x", "0").strip() or "0"
            y_raw = request.POST.get("y", "0").strip() or "0"
            shape = request.POST.get("shape", "circle").strip() or "circle"
            room = request.POST.get("room", "PISO_1").strip() or "PISO_1"
            is_contiguous_group = request.POST.get("is_contiguous_group", "").strip()
            disabled = request.POST.get("disabled") == "on"
            try:
                number = int(number_raw)
                capacity = int(capacity_raw)
                x = float(x_raw)
                y = float(y_raw)
                if capacity not in [2, 4, 6, 12]:
                    raise ValueError("Capacidad debe ser 2, 4, 6 o 12")
                if room not in ["VIP", "TERRAZA", "PISO_1"]:
                    raise ValueError("Sala debe ser VIP, Terraza o Piso 1")
                if number <= 0:
                    raise ValueError
            except (ValueError, TypeError) as exc:
                messages.error(request, f"Datos de mesa inválidos: {exc}")
                return redirect("core:admin_tables")
            if Table.objects.filter(number=number).exists():
                messages.error(request, f"Ya existe la mesa Nº {number}.")
                return redirect("core:admin_tables")
            table = Table.objects.create(
                number=number, capacity=capacity, room=room, x=x, y=y,
                shape=shape, is_contiguous_group=is_contiguous_group, disabled=disabled
            )
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="Table", object_id=table.pk, detail=f"Mesa creada Nº{number} cap {capacity} sala {room} pos({x},{y}) {shape}")
            messages.success(request, f"Mesa Nº {number} creada en {table.get_room_display()}.")
            return redirect("core:admin_tables")

        if action == "update":
            table_id = request.POST.get("table_id")
            table = get_object_or_404(Table, pk=table_id)
            number_raw = request.POST.get("number", "").strip()
            capacity_raw = request.POST.get("capacity", "").strip()
            x_raw = request.POST.get("x", "0").strip() or "0"
            y_raw = request.POST.get("y", "0").strip() or "0"
            shape = request.POST.get("shape", "circle").strip() or "circle"
            room = request.POST.get("room", "PISO_1").strip() or "PISO_1"
            is_contiguous_group = request.POST.get("is_contiguous_group", "").strip()
            disabled = request.POST.get("disabled") == "on"
            try:
                number = int(number_raw)
                capacity = int(capacity_raw)
                x = float(x_raw)
                y = float(y_raw)
                if capacity not in [2, 4, 6, 12]:
                    raise ValueError("Capacidad debe ser 2, 4, 6 o 12")
                if room not in ["VIP", "TERRAZA", "PISO_1"]:
                    raise ValueError("Sala debe ser VIP, Terraza o Piso 1")
            except (ValueError, TypeError) as exc:
                messages.error(request, f"Datos inválidos: {exc}")
                return redirect("core:admin_tables")
            if Table.objects.filter(number=number).exclude(pk=table.pk).exists():
                messages.error(request, f"Ya existe otra mesa con Nº {number}.")
                return redirect("core:admin_tables")
            table.number = number
            table.capacity = capacity
            table.room = room
            table.x = x
            table.y = y
            table.shape = shape
            table.is_contiguous_group = is_contiguous_group
            table.disabled = disabled
            table.save()
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="Table", object_id=table.pk, detail=f"Mesa Nº{number} actualizada cap {capacity} sala {room} pos({x},{y})")
            messages.success(request, f"Mesa Nº {number} actualizada.")
            return redirect("core:admin_tables")

        if action == "toggle_disabled":
            table_id = request.POST.get("table_id")
            table = get_object_or_404(Table, pk=table_id)
            table.disabled = not table.disabled
            table.save(update_fields=["disabled"])
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="Table", object_id=table.pk, detail=f"Mesa Nº{table.number} {'deshabilitada' if table.disabled else 'habilitada'}")
            messages.success(request, f"Mesa Nº {table.number} {'deshabilitada' if table.disabled else 'habilitada'}.")
            return redirect("core:admin_tables")

        if action == "delete":
            table_id = request.POST.get("table_id")
            table = get_object_or_404(Table, pk=table_id)
            if table.reservations.exists() or table.orders.exists():
                messages.error(request, f"No se puede eliminar la mesa Nº {table.number} porque tiene reservas o comandas asociadas. Deshabilítela en su lugar.")
                return redirect("core:admin_tables")
            number = table.number
            table.delete()
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="Table", object_id="", detail=f"Mesa eliminada Nº{number}")
            messages.success(request, f"Mesa Nº {number} eliminada.")
            return redirect("core:admin_tables")

        if action == "update_position":
            table_id = request.POST.get("table_id")
            x_raw = request.POST.get("x", "0").strip() or "0"
            y_raw = request.POST.get("y", "0").strip() or "0"
            try:
                x = float(x_raw)
                y = float(y_raw)
                # limitar a sala 0..30
                if x < 0 or y < 0 or x > 40 or y > 30:
                    raise ValueError("Coordenadas fuera de la sala (0–40, 0–30)")
            except (ValueError, TypeError) as exc:
                is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.headers.get("x-requested-with") == "XMLHttpRequest"
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({"ok": False, "error": str(exc)}, status=400)
                messages.error(request, f"Posición inválida: {exc}")
                return redirect("core:admin_tables")
            table = get_object_or_404(Table, pk=table_id)
            table.x = x
            table.y = y
            table.save(update_fields=["x", "y"])
            AuditLog.log(request.user, ActionType.RESERVATION, Result.SUCCESS,
                         object_type="Table", object_id=table.pk, detail=f"Mesa Nº{table.number} reubicada a ({x},{y})")
            is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.headers.get("x-requested-with") == "XMLHttpRequest"
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({"ok": True, "x": x, "y": y, "number": table.number})
            messages.success(request, f"Mesa Nº {table.number} reubicada a ({x}, {y}).")
            return redirect("core:admin_tables")

        messages.error(request, "Acción no reconocida.")
        return redirect("core:admin_tables")

    from reservations.models import Table
    tables = Table.objects.all().order_by("number")
    return render(request, "core/admin_tables.html", {"tables": tables})


@login_required
def admin_inventory(request):
    """Gestión de inventario + recetas (insumos y fichas técnicas) — solo ADMIN."""
    blocked = _guard_admin(request)
    if blocked:
        return blocked
    from audit.models import ActionType, AuditLog, Result
    from inventory.models import Ingredient, TechnicalSheet, TechnicalSheetItem
    from kitchen.models import Dish
    from decimal import Decimal, InvalidOperation

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        # --- Insumos ---
        if action == "create_ingredient":
            name = request.POST.get("name", "").strip()
            unit = request.POST.get("unit", "").strip()
            stock_raw = request.POST.get("current_stock", "0").strip() or "0"
            min_raw = request.POST.get("min_stock", "0").strip() or "0"
            cost_raw = request.POST.get("average_cost", "0").strip() or "0"
            active = request.POST.get("active") == "on"
            if not name or not unit:
                messages.error(request, "Nombre y unidad del insumo son obligatorios.")
                return redirect("core:admin_inventory")
            try:
                stock = Decimal(stock_raw)
                min_stock = Decimal(min_raw)
                cost = Decimal(cost_raw)
                if stock < 0 or min_stock < 0 or cost < 0:
                    raise ValueError
            except (InvalidOperation, ValueError, TypeError):
                messages.error(request, "Valores numéricos inválidos para stock/costo.")
                return redirect("core:admin_inventory")
            if Ingredient.objects.filter(name__iexact=name).exists():
                messages.error(request, f"Ya existe un insumo con el nombre «{name}».")
                return redirect("core:admin_inventory")
            ing = Ingredient.objects.create(name=name, unit=unit, current_stock=stock, min_stock=min_stock, average_cost=cost, active=active)
            AuditLog.log(request.user, ActionType.INVENTORY_CORRECTION, Result.SUCCESS,
                         object_type="Ingredient", object_id=ing.pk, detail=f"Insumo creado: {name} ({unit}) stock {stock} costo ${cost}")
            messages.success(request, f"Insumo «{name}» creado.")
            return redirect("core:admin_inventory")

        if action == "update_ingredient":
            ing_id = request.POST.get("ingredient_id")
            ing = get_object_or_404(Ingredient, pk=ing_id)
            name = request.POST.get("name", "").strip()
            unit = request.POST.get("unit", "").strip()
            stock_raw = request.POST.get("current_stock", "0").strip() or "0"
            min_raw = request.POST.get("min_stock", "0").strip() or "0"
            cost_raw = request.POST.get("average_cost", "0").strip() or "0"
            active = request.POST.get("active") == "on"
            if not name or not unit:
                messages.error(request, "Nombre y unidad son obligatorios.")
                return redirect("core:admin_inventory")
            try:
                stock = Decimal(stock_raw)
                min_stock = Decimal(min_raw)
                cost = Decimal(cost_raw)
            except (InvalidOperation, ValueError, TypeError):
                messages.error(request, "Valores numéricos inválidos.")
                return redirect("core:admin_inventory")
            if Ingredient.objects.filter(name__iexact=name).exclude(pk=ing.pk).exists():
                messages.error(request, f"Ya existe otro insumo con el nombre «{name}».")
                return redirect("core:admin_inventory")
            ing.name = name
            ing.unit = unit
            ing.current_stock = stock
            ing.min_stock = min_stock
            ing.average_cost = cost
            ing.active = active
            ing.save()
            AuditLog.log(request.user, ActionType.INVENTORY_CORRECTION, Result.SUCCESS,
                         object_type="Ingredient", object_id=ing.pk, detail=f"Insumo actualizado: {name} stock {stock}")
            messages.success(request, f"Insumo «{name}» actualizado.")
            return redirect("core:admin_inventory")

        if action == "delete_ingredient":
            ing_id = request.POST.get("ingredient_id")
            ing = get_object_or_404(Ingredient, pk=ing_id)
            if ing.receipts.exists() or TechnicalSheetItem.objects.filter(ingredient=ing).exists():
                messages.error(request, f"No se puede eliminar «{ing.name}» porque está usado en recepciones o recetas. Desactívelo en su lugar.")
                return redirect("core:admin_inventory")
            name = ing.name
            ing.delete()
            AuditLog.log(request.user, ActionType.INVENTORY_CORRECTION, Result.SUCCESS,
                         object_type="Ingredient", object_id="", detail=f"Insumo eliminado: {name}")
            messages.success(request, f"Insumo «{name}» eliminado.")
            return redirect("core:admin_inventory")

        if action == "toggle_ingredient":
            ing_id = request.POST.get("ingredient_id")
            ing = get_object_or_404(Ingredient, pk=ing_id)
            ing.active = not ing.active
            ing.save(update_fields=["active"])
            AuditLog.log(request.user, ActionType.INVENTORY_CORRECTION, Result.SUCCESS,
                         object_type="Ingredient", object_id=ing.pk, detail=f"Insumo {'activado' if ing.active else 'desactivado'}: {ing.name}")
            messages.success(request, f"Insumo «{ing.name}» {'activado' if ing.active else 'desactivado'}.")
            return redirect("core:admin_inventory")

        # --- Fichas técnicas / Recetas ---
        if action == "create_sheet":
            dish_id = request.POST.get("dish_id")
            dish = get_object_or_404(Dish, pk=dish_id)
            if hasattr(dish, "sheet"):
                messages.error(request, f"El platillo «{dish.name}» ya tiene una receta.")
                return redirect("core:admin_inventory")
            TechnicalSheet.objects.create(dish=dish)
            AuditLog.log(request.user, ActionType.INVENTORY_CORRECTION, Result.SUCCESS,
                         object_type="TechnicalSheet", object_id=dish.pk, detail=f"Receta creada para platillo: {dish.name}")
            messages.success(request, f"Receta creada para «{dish.name}». Agregue los insumos.")
            return redirect("core:admin_inventory")

        if action == "delete_sheet":
            sheet_id = request.POST.get("sheet_id")
            sheet = get_object_or_404(TechnicalSheet, pk=sheet_id)
            dish_name = sheet.dish.name
            sheet.delete()
            AuditLog.log(request.user, ActionType.INVENTORY_CORRECTION, Result.SUCCESS,
                         object_type="TechnicalSheet", object_id="", detail=f"Receta eliminada: {dish_name}")
            messages.success(request, f"Receta de «{dish_name}» eliminada.")
            return redirect("core:admin_inventory")

        if action == "add_sheet_item":
            sheet_id = request.POST.get("sheet_id")
            ingredient_id = request.POST.get("ingredient_id")
            qty_raw = request.POST.get("quantity", "").strip()
            sheet = get_object_or_404(TechnicalSheet, pk=sheet_id)
            ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
            try:
                qty = Decimal(qty_raw)
                if qty <= 0:
                    raise ValueError
            except (InvalidOperation, ValueError, TypeError):
                messages.error(request, "Cantidad inválida para el insumo.")
                return redirect("core:admin_inventory")
            if TechnicalSheetItem.objects.filter(sheet=sheet, ingredient=ingredient).exists():
                messages.error(request, f"«{ingredient.name}» ya está en la receta de «{sheet.dish.name}». Edite la cantidad existente.")
                return redirect("core:admin_inventory")
            TechnicalSheetItem.objects.create(sheet=sheet, ingredient=ingredient, quantity=qty)
            AuditLog.log(request.user, ActionType.INVENTORY_CORRECTION, Result.SUCCESS,
                         object_type="TechnicalSheetItem", object_id=sheet.pk, detail=f"Ingrediente {ingredient.name} ×{qty} agregado a {sheet.dish.name}")
            messages.success(request, f"Insumo «{ingredient.name}» agregado a la receta de «{sheet.dish.name}».")
            return redirect("core:admin_inventory")

        if action == "update_sheet_item":
            item_id = request.POST.get("item_id")
            qty_raw = request.POST.get("quantity", "").strip()
            item = get_object_or_404(TechnicalSheetItem, pk=item_id)
            try:
                qty = Decimal(qty_raw)
                if qty <= 0:
                    raise ValueError
            except (InvalidOperation, ValueError, TypeError):
                messages.error(request, "Cantidad inválida.")
                return redirect("core:admin_inventory")
            item.quantity = qty
            item.save(update_fields=["quantity"])
            AuditLog.log(request.user, ActionType.INVENTORY_CORRECTION, Result.SUCCESS,
                         object_type="TechnicalSheetItem", object_id=item.pk, detail=f"Cantidad actualizada {item.ingredient.name} ×{qty} en {item.sheet.dish.name}")
            messages.success(request, "Cantidad actualizada.")
            return redirect("core:admin_inventory")

        if action == "remove_sheet_item":
            item_id = request.POST.get("item_id")
            item = get_object_or_404(TechnicalSheetItem, pk=item_id)
            name = item.ingredient.name
            dish_name = item.sheet.dish.name
            item.delete()
            AuditLog.log(request.user, ActionType.INVENTORY_CORRECTION, Result.SUCCESS,
                         object_type="TechnicalSheetItem", object_id="", detail=f"Ingrediente {name} eliminado de receta {dish_name}")
            messages.success(request, f"Insumo «{name}» eliminado de la receta de «{dish_name}».")
            return redirect("core:admin_inventory")

        messages.error(request, "Acción no reconocida.")
        return redirect("core:admin_inventory")

    ingredients = Ingredient.objects.all().order_by("name")
    sheets = TechnicalSheet.objects.select_related("dish").prefetch_related("ingredients__ingredient").order_by("dish__name")
    dishes = Dish.objects.all().order_by("name")
    dishes_without_sheet = [d for d in dishes if not hasattr(d, "sheet")]
    sheets_by_dish = set(sheets.values_list("dish_id", flat=True))
    total_value = sum(i.current_stock * i.average_cost for i in ingredients)
    return render(request, "core/admin_inventory.html", {
        "ingredients": ingredients,
        "sheets": sheets,
        "dishes": dishes,
        "dishes_without_sheet": dishes_without_sheet,
        "sheets_by_dish": sheets_by_dish,
        "total_value": total_value,
    })