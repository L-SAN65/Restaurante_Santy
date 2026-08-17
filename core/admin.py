from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BusinessConfig, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "role", "first_name", "is_active", "is_permanently_locked")
    list_filter = ("role", "is_active", "is_permanently_locked")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos personales", {"fields": ("first_name", "last_name", "cedula")}),
        ("Rol", {"fields": ("role",)}),
        (
            "Control de acceso",
            {
                "fields": (
                    "failed_login_count",
                    "suspended_until",
                    "is_permanently_locked",
                )
            },
        ),
        (
            "Permisos",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Fechas",
            {"fields": ("last_login", "date_joined")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "cedula"),
            },
        ),
    )


@admin.register(BusinessConfig)
class BusinessConfigAdmin(admin.ModelAdmin):
    list_display = (
        "vat_rate",
        "operating_timezone",
        "min_reservation_hours",
        "cash_tolerance",
        "pin_ttl_seconds",
    )