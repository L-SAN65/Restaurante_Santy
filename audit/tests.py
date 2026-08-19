from django.test import TestCase
from django.urls import reverse

from audit.models import AuditLog, PinToken
from core.models import BusinessConfig, Role, User


class AuditViewTest(TestCase):
    def setUp(self):
        BusinessConfig.objects.get_or_create(pk=1, defaults={"pin_ttl_seconds": 60})
        self.admin = User.objects.create_user(
            username="admin@test.com", password="pass", role=Role.ADMIN, is_staff=True
        )
        self.cashier = User.objects.create_user(
            username="cashier@test.com", password="pass", role=Role.CASHIER
        )

    def test_trail_200_for_admin(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("audit:trail"))
        self.assertEqual(resp.status_code, 200)

    def test_trail_denied_for_cashier(self):
        self.client.force_login(self.cashier)
        resp = self.client.get(reverse("audit:trail"))
        self.assertRedirects(resp, reverse("core:cashier_dashboard"))

    def test_pin_generate_and_validate(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("audit:pin"), {"action": "Anular factura"})
        token = PinToken.objects.first()
        self.assertIsNotNone(token)
        self.assertTrue(token.is_valid)

        resp = self.client.post(reverse("audit:pin_validate"), {"code": token.code})
        self.assertRedirects(resp, reverse("audit:pin"))
        token.refresh_from_db()
        self.assertFalse(token.is_valid)