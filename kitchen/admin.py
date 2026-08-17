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
    list_display = ("name", "price", "availability", "active")
    list_filter = ("availability",)