from django.urls import path

from .views import (
    CustomLogoutView,
    admin_dashboard,
    admin_dishes,
    admin_inventory,
    admin_tables,
    cashier_dashboard,
    chef_dashboard,
    client_login_view,
    dashboard,
    login_view,
    user_management,
    waiter_dashboard,
    warehouse_dashboard,
)

app_name = "core"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/admin/usuarios/", user_management, name="user_management"),
    path("dashboard/admin/platos/", admin_dishes, name="admin_dishes"),
    path("dashboard/admin/mesas/", admin_tables, name="admin_tables"),
    path("dashboard/admin/inventario-recetas/", admin_inventory, name="admin_inventory"),
    path("dashboard/cajero/", cashier_dashboard, name="cashier_dashboard"),
    path("dashboard/mesero/", waiter_dashboard, name="waiter_dashboard"),
    path("dashboard/chef/", chef_dashboard, name="chef_dashboard"),
    path("dashboard/bodega/", warehouse_dashboard, name="warehouse_dashboard"),
]