from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("reservas/", include("reservations.urls")),
    path("facturacion/", include("billing.urls")),
    path("cocina/", include("kitchen.urls")),
    path("inventario/", include("inventory.urls")),
    path("fidelizacion/", include("loyalty.urls")),
    path("auditoria/", include("audit.urls")),
]