from django.contrib import admin

from .models import AuditLog, PinToken


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "result", "object_type", "object_id")
    list_filter = ("action", "result", "timestamp")
    search_fields = ("user__email", "object_id", "detail")
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(PinToken)
class PinTokenAdmin(admin.ModelAdmin):
    list_display = ("code", "issued_by", "issued_at", "valid_until", "consumed_at")
    readonly_fields = [f.name for f in PinToken._meta.fields]

    def has_add_permission(self, request):
        return False