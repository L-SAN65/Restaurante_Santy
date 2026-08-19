from django.urls import path

from .views import (
    correction_review,
    corrections,
    dashboard,
    receipt_confirm,
    receipts,
)

app_name = "inventory"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("recepciones/", receipts, name="receipts"),
    path("recepciones/<int:receipt_id>/confirmar/", receipt_confirm, name="receipt_confirm"),
    path("correcciones/", corrections, name="corrections"),
    path("correcciones/<int:correction_id>/revisar/", correction_review, name="correction_review"),
]