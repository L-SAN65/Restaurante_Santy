from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="core:login", permanent=False)),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("reservas/", include("reservations.urls")),
    path("facturacion/", include("billing.urls")),
    path("cocina/", include("kitchen.urls")),
    path("inventario/", include("inventory.urls")),
    path("fidelizacion/", include("loyalty.urls")),
    path("auditoria/", include("audit.urls")),
]