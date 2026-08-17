from django.urls import path

from .views import audit_trail

app_name = "audit"

urlpatterns = [
    path("", audit_trail, name="trail"),
]