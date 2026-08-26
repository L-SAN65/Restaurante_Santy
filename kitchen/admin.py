from django.contrib import admin

from .models import Dish, Order, OrderItem, Shrinkage


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "table", "waiter", "status", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]


@admin.register(Shrinkage)
class ShrinkageAdmin(admin.ModelAdmin):
    list_display = ("id", "order_item", "reason", "registered_by", "registered_at")
    readonly_fields = ("registered_at",)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "availability", "active", "image_preview")
    list_filter = ("availability", "active")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="height:56px;width:80px;object-fit:cover;border-radius:8px;border:1px solid #e5e1d8;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Imagen"