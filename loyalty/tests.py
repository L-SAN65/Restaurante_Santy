from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import BusinessConfig, Role, User
from loyalty.models import LoyaltyMovement, MovementType


class LoyaltyViewTest(TestCase):
    def setUp(self):
        BusinessConfig.objects.get_or_create(pk=1)
        self.cashier = User.objects.create_user(
            username="cashier@test.com", password="pass", role=Role.CASHIER
        )
        LoyaltyMovement.objects.create(
            client_cedula="8-555-666",
            movement_type=MovementType.ACCRUAL,
            points=120,
            expires_at=timezone.now() + timedelta(days=60),
        )

    def test_wallet_shows_balance_for_cedula(self):
        self.client.force_login(self.cashier)
        resp = self.client.get(reverse("loyalty:wallet"), {"cedula": "8-555-666"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "120")

    def test_redeem_applies_discount(self):
        self.client.force_login(self.cashier)
        resp = self.client.post(reverse("loyalty:redeem"), {
            "cedula": "8-555-666",
            "points": "50",
            "subtotal": "100",
        })
        self.assertRedirects(resp, reverse("loyalty:wallet"))
        self.assertEqual(LoyaltyMovement.balance("8-555-666"), 70)

    def test_redeem_rejected_without_balance(self):
        self.client.force_login(self.cashier)
        resp = self.client.post(reverse("loyalty:redeem"), {
            "cedula": "8-555-666",
            "points": "500",
            "subtotal": "100",
        })
        self.assertRedirects(resp, reverse("loyalty:wallet"))
        self.assertEqual(LoyaltyMovement.balance("8-555-666"), 120)