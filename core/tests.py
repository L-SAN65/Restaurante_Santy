from django.test import TestCase
from django.urls import reverse

from core.models import BusinessConfig, Role, User


class CoreAuthFlowTest(TestCase):
    def setUp(self):
        BusinessConfig.objects.get_or_create(pk=1)
        self.admin = User.objects.create_user(
            username="admin@test.com", password="pass", role=Role.ADMIN, is_staff=True
        )
        self.waiter = User.objects.create_user(
            username="waiter@test.com", password="pass", role=Role.WAITER
        )
        self.chef = User.objects.create_user(
            username="chef@test.com", password="pass", role=Role.CHEF
        )
        self.cashier = User.objects.create_user(
            username="cashier@test.com", password="pass", role=Role.CASHIER
        )
        self.warehouse = User.objects.create_user(
            username="bodega@test.com", password="pass", role=Role.WAREHOUSE
        )

    def test_login_redirects_by_role(self):
        cases = [
            (self.admin, "core:admin_dashboard"),
            (self.waiter, "core:waiter_dashboard"),
            (self.chef, "core:chef_dashboard"),
            (self.cashier, "core:cashier_dashboard"),
            (self.warehouse, "core:warehouse_dashboard"),
        ]
        for user, expected in cases:
            self.client.logout()
            resp = self.client.post(reverse("core:login"), {
                "username": user.username,
                "password": "pass",
            })
            self.assertRedirects(resp, reverse(expected))

    def test_waiter_cannot_access_admin_dashboard(self):
        self.client.force_login(self.waiter)
        resp = self.client.get(reverse("core:admin_dashboard"))
        self.assertRedirects(resp, reverse("core:waiter_dashboard"))

    def test_dashboards_render_200_for_each_role(self):
        cases = [
            (self.admin, "core:admin_dashboard"),
            (self.waiter, "core:waiter_dashboard"),
            (self.chef, "core:chef_dashboard"),
            (self.cashier, "core:cashier_dashboard"),
            (self.warehouse, "core:warehouse_dashboard"),
        ]
        for user, name in cases:
            self.client.force_login(user)
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get(reverse("core:admin_dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("core:login"), resp.url)