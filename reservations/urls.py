from django.urls import path

from .views import (
    cancel_reservation,
    my_reservations,
    reservation_detail,
    reservation_portal,
    table_list,
)

app_name = "reservations"

urlpatterns = [
    path("", reservation_portal, name="portal"),
    path("mis-reservas/", my_reservations, name="my_reservations"),
    path("mis-reservas/<int:reservation_id>/cancelar/", cancel_reservation, name="cancel"),
    path("api/tables/", table_list, name="tables_api"),
    path("<int:reservation_id>/", reservation_detail, name="detail"),
]