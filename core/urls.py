from django.urls import path

from .views import (
    CustomLogoutView,
    admin_dashboard,
    cashier_dashboard,
    chef_dashboard,
    dashboard,
    login_view,
    waiter_dashboard,
    warehouse_dashboard,
    waiter_floor_plan,
    waiter_order_creation,
    waiter_account_segmentation,
    waiter_checkin,
    kds_main,
    kds_shrinkage,
    cashier_billing,
    cashier_cash_closing,
    inventory_dashboard,
    kds_api,
    shrinkage_api,
    inventory_stats_api,
    inventory_history_api,
    checkin_api,
    billing_api,
    table_list,
)

app_name = "core"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/cajero/", cashier_dashboard, name="cashier_dashboard"),
    path("dashboard/mesero/", waiter_dashboard, name="waiter_dashboard"),
    path("dashboard/chef/", chef_dashboard, name="chef_dashboard"),
    path("dashboard/bodega/", warehouse_dashboard, name="warehouse_dashboard"),
    # Waiter routes
    path("mesero/plano-salas/", waiter_floor_plan, name="waiter_floor_plan"),
    path("mesero/comanda/nueva/", waiter_order_creation, name="waiter_order_creation"),
    path("mesero/segmentar-cuenta/", waiter_account_segmentation, name="waiter_account_segmentation"),
    path("mesero/check-in/", waiter_checkin, name="waiter_checkin"),
    # KDS routes
    path("kds/", kds_main, name="kds_main"),
    path("kds/mermas/", kds_shrinkage, name="kds_shrinkage"),
    # Billing routes
    path("facturacion/", cashier_billing, name="cashier_billing"),
    path("facturacion/cerrar-caja/", cashier_cash_closing, name="cashier_cash_closing"),
    # Inventory routes
    path("inventario/", inventory_dashboard, name="inventory_dashboard"),
    # API routes
    path("api/kds/", kds_api, name="kds_api"),
    path("api/shrinkage/", shrinkage_api, name="shrinkage_api"),
    path("api/inventory/stats/", inventory_stats_api, name="inventory_stats_api"),
    path("api/inventory/history/", inventory_history_api, name="inventory_history_api"),
    path("api/checkin/", checkin_api, name="checkin_api"),
    path("api/billing/", billing_api, name="billing_api"),
    path("api/tables/", table_list, name="table_list"),
]