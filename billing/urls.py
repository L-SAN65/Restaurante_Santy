from django.urls import path

from .views import (
    cash_register_close,
    cash_register_open,
    reports_export_excel,
    reports_export_pdf,
    reports_view,
)

app_name = "billing"

urlpatterns = [
    path("reportes/", reports_view, name="reports"),
    path("reportes/exportar/pdf/", reports_export_pdf, name="reports_export_pdf"),
    path("reportes/exportar/excel/", reports_export_excel, name="reports_export_excel"),
    path("caja/abrir/", cash_register_open, name="cash_register_open"),
    path("caja/cerrar/", cash_register_close, name="cash_register_close"),
]