from django.contrib import admin

from .models import LoyaltyMovement


@admin.register(LoyaltyMovement)
class LoyaltyMovementAdmin(admin.ModelAdmin):
    list_display = ("id", "client_cedula", "movement_type", "points", "created_at", "expires_at")
    list_filter = ("movement_type",)
    readonly_fields = ("created_at",)