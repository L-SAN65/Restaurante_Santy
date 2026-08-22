from django.urls import path

from core.views import client_login_view, client_register_view
from .views import (
    cancel_reservation,
    checkin,
    floor_plan,
    menu_public,
    my_reservations,
    no_show,
    reservation_confirm,
    reservation_detail,
    reservation_portal,
    reservation_success,
    reservation_tables,
    table_list,
)

app_name = "reservations"

urlpatterns = [
    path("menu/", menu_public, name="menu"),
    path("login/", client_login_view, name="client_login"),
    path("registro/", client_register_view, name="client_register"),
    path("", reservation_portal, name="portal"),
    path("mesas/", reservation_tables, name="table_select"),
    path("confirmar/", reservation_confirm, name="confirm"),
    path("exito/<int:reservation_id>/", reservation_success, name="success"),
    path("mis-reservas/", my_reservations, name="my_reservations"),
    path("mis-reservas/<int:reservation_id>/cancelar/", cancel_reservation, name="cancel"),
    path("api/tables/", table_list, name="tables_api"),
    path("<int:reservation_id>/", reservation_detail, name="detail"),
    # Sala / Mesero
    path("sala/plano/", floor_plan, name="floor_plan"),
    path("sala/checkin/", checkin, name="checkin"),
    path("sala/no-show/", no_show, name="no_show"),
]