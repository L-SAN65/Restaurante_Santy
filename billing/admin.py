from django.contrib import admin

from .models import CashRegister, Invoice


@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ("id", "opened_by", "status", "opening_fund", "opened_at", "closed_at")
    list_filter = ("status",)
    readonly_fields = ("opened_at",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "client_cedula", "subtotal", "vat_amount", "total", "status")
    list_filter = ("status", "payment_type")
    readonly_fields = ("issued_at",)