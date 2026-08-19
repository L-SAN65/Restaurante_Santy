from django.urls import path

from .views import (
    account_segmentation,
    kds,
    order_create,
    order_delivered,
    order_ready,
    order_start,
    shrinkage,
)

app_name = "kitchen"

urlpatterns = [
    # KDS
    path("", kds, name="kds"),
    path("comandas/<int:order_id>/iniciar/", order_start, name="order_start"),
    path("comandas/<int:order_id>/listo/", order_ready, name="order_ready"),
    path("comandas/<int:order_id>/entregado/", order_delivered, name="order_delivered"),
    path("comandas/<int:order_id>/merma/", shrinkage, name="shrinkage"),
    # Mesero
    path("mesa/<int:table_id>/comanda/", order_create, name="order_create"),
    path("comandas/<int:order_id>/segmentar/", account_segmentation, name="account_segmentation"),
]