from django.contrib import admin

from .models import Reservation, Table, TableBlock


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number", "capacity", "room", "x", "y", "is_contiguous_group", "disabled")
    list_filter = ("room", "capacity", "disabled")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "client_email", "guests", "start_at", "end_at", "status")
    list_filter = ("status", "start_at")
    filter_horizontal = ("tables",)


@admin.register(TableBlock)
class TableBlockAdmin(admin.ModelAdmin):
    list_display = ("token", "created_at", "expires_at", "confirmed")
    filter_horizontal = ("tables",)
    readonly_fields = ("token", "created_at")