from django.urls import path

from .views import audit_trail, pin_generate, pin_validate

app_name = "audit"

urlpatterns = [
    path("", audit_trail, name="trail"),
    path("pin/", pin_generate, name="pin"),
    path("pin/validar/", pin_validate, name="pin_validate"),
]