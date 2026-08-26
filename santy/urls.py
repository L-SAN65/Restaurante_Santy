from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # Landing público: menú accesible sin login (QR / digital) — primer paso del flujo cliente
    path("", RedirectView.as_view(pattern_name="reservations:menu", permanent=False)),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("reservas/", include("reservations.urls")),
    path("facturacion/", include("billing.urls")),
    path("cocina/", include("kitchen.urls")),
    path("inventario/", include("inventory.urls")),
    path("fidelizacion/", include("loyalty.urls")),
    path("auditoria/", include("audit.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)