from django.contrib import admin

from .models import (
    CorrectionRequest,
    Ingredient,
    Receipt,
    TechnicalSheet,
    TechnicalSheetItem,
)


class TechnicalSheetItemInline(admin.TabularInline):
    model = TechnicalSheetItem
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "current_stock", "min_stock", "average_cost", "active")
    list_filter = ("active",)


@admin.register(TechnicalSheet)
class TechnicalSheetAdmin(admin.ModelAdmin):
    list_display = ("dish", "updated_at")
    inlines = [TechnicalSheetItemInline]


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("id", "ingredient", "quantity", "unit_cost", "lot", "confirmed")
    list_filter = ("confirmed",)


@admin.register(CorrectionRequest)
class CorrectionRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "receipt", "difference_quantity", "status", "created_at")
    list_filter = ("status",)