from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from audit.models import ActionType, AuditLog, PinToken, Result
from billing.models import (
    CashRegister,
    CashRegisterStatus,
    Invoice,
    InvoiceStatus,
    PaymentType,
)
from core.models import BusinessConfig, Role, User
from kitchen.models import Order, OrderItem, OrderStatus
from loyalty.models import LoyaltyMovement
from reservations.models import Table


class BillingViewTest(TestCase):
    def setUp(self):
        config, _ = BusinessConfig.objects.get_or_create(pk=1, defaults={"vat_rate": "0.15"})
        config.vat_rate = "0.15"
        config.save()
        self.admin = User.objects.create_user(
            username="admin@test.com", password="pass", role=Role.ADMIN, is_staff=True
        )
        self.cashier = User.objects.create_user(
            username="cashier@test.com", password="pass", role=Role.CASHIER
        )
        self.waiter = User.objects.create_user(
            username="waiter@test.com", password="pass", role=Role.WAITER
        )
        self.table = Table.objects.create(number=1, capacity=4)

    def _make_delivered_order(self):
        order = Order.objects.create(
            table=self.table, waiter=self.waiter, status=OrderStatus.DELIVERED
        )
        OrderItem.objects.create(
            order=order, name="Arroz con pollo", quantity=2, unit_price="50.00"
        )
        return order

    def test_invoice_create_computes_vat(self):
        self.client.force_login(self.cashier)
        order = self._make_delivered_order()
        resp = self.client.post(reverse("billing:invoice_create", args=[order.pk]), {
            "client_name": "Juan",
            "client_cedula": "8-111-222",
            "paid_amount": "115.00",
        })
        self.assertRedirects(resp, reverse("billing:invoice_list"))
        invoice = Invoice.objects.get(order=order)
        self.assertEqual(invoice.status, InvoiceStatus.ISSUED)
        self.assertEqual(float(invoice.subtotal), 100.00)
        self.assertEqual(float(invoice.vat_amount), 15.00)
        self.assertEqual(float(invoice.total), 115.00)
        self.assertEqual(invoice.payment_type, PaymentType.FULL)

    def test_partial_payment_keeps_balance(self):
        self.client.force_login(self.cashier)
        order = self._make_delivered_order()
        self.client.post(reverse("billing:invoice_create", args=[order.pk]), {
            "client_name": "Ana",
            "client_cedula": "8-333-444",
            "paid_amount": "70.00",
        })
        invoice = Invoice.objects.get(order=order)
        self.assertEqual(invoice.payment_type, PaymentType.PARTIAL)
        self.assertEqual(float(invoice.remaining_balance), 45.00)

    def test_annulment_requires_admin_and_valid_pin(self):
        order = self._make_delivered_order()
        invoice = Invoice.objects.create(
            order=order,
            client_name="Juan",
            subtotal="100.00",
            vat_rate="0.15",
            vat_amount="15.00",
            total="115.00",
            paid_amount="115.00",
            status=InvoiceStatus.DRAFT,
        )
        invoice.issue()

        # Cajero no puede anular
        self.client.force_login(self.cashier)
        resp = self.client.post(reverse("billing:invoice_annul", args=[invoice.pk]), {"pin": "000000"})
        self.assertEqual(resp.status_code, 302)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, InvoiceStatus.ISSUED)

        # Admin con PIN vigente sí puede
        self.client.force_login(self.admin)
        token = PinToken.objects.create(
            code="123456",
            issued_by=self.admin,
            valid_until=timezone.now() + timedelta(seconds=60),
        )
        resp = self.client.post(reverse("billing:invoice_annul", args=[invoice.pk]), {"pin": "123456"})
        self.assertRedirects(resp, reverse("audit:trail"))
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, InvoiceStatus.ANNULLED)
        self.assertTrue(AuditLog.objects.filter(action=ActionType.ANULATION, object_id=str(invoice.pk), result=Result.SUCCESS).exists())

    def test_register_open_rejects_zero(self):
        self.client.force_login(self.cashier)
        resp = self.client.post(reverse("billing:cash_register_open"), {"opening_fund": "0"})
        self.assertFalse(CashRegister.objects.filter(status=CashRegisterStatus.OPEN).exists())

    def test_blind_close_squared_within_tolerance(self):
        register = CashRegister.objects.create(
            opened_by=self.cashier, opening_fund=100, status=CashRegisterStatus.OPEN
        )
        self.client.force_login(self.cashier)
        resp = self.client.post(reverse("billing:cash_register_close"), {"declared_cash": "100"})
        register.refresh_from_db()
        self.assertEqual(register.status, CashRegisterStatus.SQUARED)