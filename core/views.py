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
    from django.db.models import Count
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
    critical = sum(
        1 for ing in ingredients if ing.current_stock < ing.min_stock
    )
    totals = {
        "total_ingredients": ingredients.count(),
        "critical": critical,
        "sheets": TechnicalSheet.objects.count(),
        "total_value": sum(ing.current_stock * ing.average_cost for ing in ingredients),
    }
    return render(request, "core/warehouse_dashboard.html", {"totals": totals})


# Waiter views
@login_required
def waiter_floor_plan(request):
    if not request.user.role == Role.WAITER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return render(request, "core/waiter_floor_plan.html")


@login_required
def waiter_order_creation(request):
    if not request.user.role == Role.WAITER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return render(request, "core/waiter_order_creation.html")


@login_required
def waiter_account_segmentation(request):
    if not request.user.role == Role.WAITER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return render(request, "core/waiter_account_segmentation.html")


@login_required
def waiter_checkin(request):
    if not request.user.role == Role.WAITER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return render(request, "core/waiter_checkin.html")


# KDS views
@login_required
def kds_main(request):
    if not request.user.role == Role.CHEF:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    from kitchen.models import Order, OrderStatus

    tickets = (
        Order.objects.filter(status__in=[OrderStatus.WAITING, OrderStatus.PREPARING])
        .select_related("table", "waiter")
        .prefetch_related("items")
    )
    return render(request, "core/kds_main.html", {"tickets": tickets})


@login_required
def kds_shrinkage(request):
    if not request.user.role == Role.CHEF:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return render(request, "core/kds_shrinkage.html")


# Billing views
@login_required
def cashier_billing(request):
    if not request.user.role == Role.CASHIER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    from reservations.models import Table

    tables = [
        {"id": t.id, "nombre": f"Mesa {t.number}", "capacity": t.capacity}
        for t in Table.objects.all()
    ]
    return render(request, "core/cashier_billing.html", {"tables": tables})


@login_required
def cashier_cash_closing(request):
    if not request.user.role == Role.CASHIER:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return redirect("billing:cash_register_close")


@login_required
def inventory_dashboard(request):
    if not request.user.role == Role.WAREHOUSE:
        messages.error(request, "No tiene permisos para acceder a este módulo.")
        return redirect(request.user.dashboard_url)
    return render(request, "core/inventory_dashboard.html")


# API endpoints
@login_required
def kds_api(request):
    from django.utils import timezone

    tickets = [
        {
            "id": 1,
            "table_number": 4,
            "order_id": "ORD-001",
            "items_count": 3,
            "started_at": timezone.now().timestamp() * 1000,
            "category": "green"
        },
        {
            "id": 2,
            "table_number": 7,
            "order_id": "ORD-002",
            "items_count": 5,
            "started_at": (timezone.now() - 600000).timestamp() * 1000,
            "category": "yellow"
        },
        {
            "id": 3,
            "table_number": 12,
            "order_id": "ORD-003",
            "items_count": 2,
            "started_at": (timezone.now() - 1800000).timestamp() * 1000,
            "category": "red"
        }
    ]

    return JsonResponse(tickets, safe=False)


@login_required
def shrinkage_api(request):
    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body)
            return JsonResponse({
                "success": True,
                "dish_name": data.get("dish_name", "Desconocido"),
                "original_charge": 15.50,
                "message": "Merma registrada y alerta enviada"
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos inválidos"}, status=400)

    if request.method == "GET":
        history = [
            {
                "id": 1,
                "dish_name": "Arroz con Pollo",
                "reason": "producto_quemado",
                "original_charge": 12.50,
                "formatted_date": "Hoy 14:30"
            },
            {
                "id": 2,
                "dish_name": "Salmón",
                "reason": "vencido",
                "original_charge": 25.00,
                "formatted_date": "Ayer 20:15"
            }
        ]
        return JsonResponse(history, safe=False)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def inventory_stats_api(request):
    if request.method == "GET":
        stats = {
            "total_value": 4580.50,
            "total_ingredients": 125,
            "critical_ingredients": 8,
            "low_stock": [
                {"name": "Aceite vegetal", "current_stock": 2, "min_stock": 5},
                {"name": "Salmón fresco", "current_stock": 3, "min_stock": 10}
            ],
            "disabled_dishes": [
                {"dish_name": "Risotto de mariscos", "missing_ingredient": "Arroz"},
                {"dish_name": "Steak au poivre", "missing_ingredient": "Filete"}
            ]
        }
        return JsonResponse(stats)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def inventory_history_api(request):
    if request.method == "GET":
        history = {
            "history": [
                {"type": "Recepción", "description": "Entrada de 5kg de arroz", "formatted_date": "Hoy 10:00"},
                {"type": "Salida", "description": "Uso en cocina: 2 platos", "formatted_date": "Hoy 12:30"},
                {"type": "Ajuste", "description": "Inventario por merma", "formatted_date": "Ayer 16:45"}
            ]
        }
        return JsonResponse(history)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def checkin_api(request):
    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body)
            cedula = data.get("cedula", "")
            real_people = data.get("real_people", 0)

            return JsonResponse({
                "success": True,
                "reservation_id": "RES-20260818-001",
                "updated_people": real_people,
                "tables_joined": 0,
                "table_status": "Ocupada"
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos inválidos"}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def billing_api(request):
    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body)
            products = data.get("products", [])
            subtotal = sum(p.get("price", 0) * p.get("qty", 1) for p in products)
            iva = subtotal * 0.15
            total = subtotal + iva

            return JsonResponse({
                "success": True,
                "invoice_number": "FAC-20260818-001",
                "subtotal": round(subtotal, 2),
                "iva": round(iva, 2),
                "total": round(total, 2),
                "table_number": data.get("table_id", "N/A"),
                "status": "Emitida"
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos inválidos"}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def table_list(request):
    import random
    tables = [
        {"id": i, "nombre": f"Mesa {i}", "capacity": [2, 4, 6, 12][i % 4]}
        for i in range(1, 25)
    ]
    for table in tables:
        if random.random() < 0.3:
            table["status"] = random.choice(["ocupada", "reservada", "bloqueada"])
        else:
            table["status"] = "disponible"

    return JsonResponse(tables, safe=False)