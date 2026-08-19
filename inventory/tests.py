from django.test import TestCase
from django.urls import reverse

from core.models import BusinessConfig, Role, User
from inventory.models import (
    CorrectionRequest,
    CorrectionRequestStatus,
    Ingredient,
    Receipt,
)
from kitchen.models import Dish


class InventoryViewTest(TestCase):
    def setUp(self):
        BusinessConfig.objects.get_or_create(pk=1)
        self.warehouse = User.objects.create_user(
            username="bodega@test.com", password="pass", role=Role.WAREHOUSE
        )
        self.admin = User.objects.create_user(
            username="admin@test.com", password="pass", role=Role.ADMIN, is_staff=True
        )
        self.ingredient = Ingredient.objects.create(
            name="Arroz", unit="kg", current_stock="10", min_stock="2", average_cost="2.00"
        )

    def test_dashboard_200_for_warehouse(self):
        self.client.force_login(self.warehouse)
        resp = self.client.get(reverse("inventory:dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Arroz")

    def test_receipt_confirm_applies_weighted_average(self):
        self.client.force_login(self.warehouse)
        resp = self.client.post(reverse("inventory:receipts"), {
            "ingredient": self.ingredient.pk,
            "quantity": "10",
            "unit_cost": "3.00",
            "lot": "LOT-01",
        })
        self.assertRedirects(resp, reverse("inventory:receipts"))
        receipt = Receipt.objects.get(ingredient=self.ingredient)
        self.assertFalse(receipt.confirmed)

        self.client.post(reverse("inventory:receipt_confirm", args=[receipt.pk]))
        self.ingredient.refresh_from_db()
        self.assertEqual(float(self.ingredient.current_stock), 20.0)
        self.assertEqual(float(self.ingredient.average_cost), 2.50)

    def test_correction_request_and_admin_approval(self):
        receipt = Receipt.objects.create(
            ingredient=self.ingredient,
            received_by=self.warehouse,
            quantity="10",
            unit_cost="3.00",
            lot="LOT-02",
            confirmed=True,
        )
        # Confirmar aplica stock
        self.ingredient.refresh_from_db()

        self.client.force_login(self.warehouse)
        resp = self.client.post(reverse("inventory:corrections"), {
            "receipt": receipt.pk,
            "difference_quantity": "-2",
            "reason": "Sobra inventario físico",
        })
        self.assertRedirects(resp, reverse("inventory:corrections"))
        req = CorrectionRequest.objects.get(receipt=receipt)
        self.assertEqual(req.status, CorrectionRequestStatus.PENDING)

        self.client.force_login(self.admin)
        self.client.post(reverse("inventory:correction_review", args=[req.pk]), {"action": "approve"})
        req.refresh_from_db()
        self.assertEqual(req.status, CorrectionRequestStatus.APPROVED)