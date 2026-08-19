from django.urls import path

from .views import (
    CustomLogoutView,
    admin_dashboard,
    cashier_dashboard,
    chef_dashboard,
    client_login_view,
    dashboard,
    login_view,
    waiter_dashboard,
    warehouse_dashboard,
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
]