from django.test import TestCase
from django.urls import reverse

from core.models import BusinessConfig, Role, User
from inventory.models import Ingredient, TechnicalSheet, TechnicalSheetItem
from kitchen.models import Dish, Order, OrderItem, OrderStatus, Shrinkage
from reservations.models import Table


class KitchenViewTest(TestCase):
    def setUp(self):
        BusinessConfig.objects.get_or_create(pk=1)
        self.chef = User.objects.create_user(
            username="chef@test.com", password="pass", role=Role.CHEF
        )
        self.waiter = User.objects.create_user(
            username="waiter@test.com", password="pass", role=Role.WAITER
        )
        self.table = Table.objects.create(number=1, capacity=4)

        self.dish = Dish.objects.create(name="Arroz con pollo", price="20.00")
        self.dish2 = Dish.objects.create(name="Salmón", price="30.00")
        self.ingredient = Ingredient.objects.create(
            name="Arroz", unit="kg", current_stock="10", min_stock="2", average_cost="2.00"
        )
        sheet = TechnicalSheet.objects.create(dish=self.dish)
        TechnicalSheetItem.objects.create(
            sheet=sheet, ingredient=self.ingredient, quantity="0.5"
        )

    def _make_order(self, status=OrderStatus.DELIVERED):
        order = Order.objects.create(table=self.table, waiter=self.waiter, status=status)
        OrderItem.objects.create(
            order=order, name="Arroz con pollo", quantity=2, unit_price="20.00"
        )
        return order

    def test_order_create_deducts_stock_and_marks_table_occupied(self):
        self.client.force_login(self.waiter)
        resp = self.client.post(
            reverse("kitchen:order_create", args=[self.table.pk]),
            {"dish_id": [self.dish.pk], "qty": [2], "notes": [""]},
        )
        self.assertRedirects(resp, reverse("reservations:floor_plan"))
        order = Order.objects.get(table=self.table)
        self.assertEqual(order.status, OrderStatus.WAITING)
        self.assertEqual(order.items.count(), 1)
        self.ingredient.refresh_from_db()
        self.assertEqual(float(self.ingredient.current_stock), 9.0)

        self.assertEqual(self.table.status, "OCCUPIED")

    def test_kds_200_for_chef(self):
        self._make_order(status=OrderStatus.WAITING)
        self.client.force_login(self.chef)
        resp = self.client.get(reverse("kitchen:kds"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Arroz con pollo")

    def test_order_start_changes_to_preparing(self):
        order = self._make_order(status=OrderStatus.WAITING)
        self.client.force_login(self.chef)
        self.client.post(reverse("kitchen:order_start", args=[order.pk]))
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.PREPARING)

    def test_shrinkage_creates_record_and_audit(self):
        order = self._make_order(status=OrderStatus.PREPARING)
        item = order.items.first()
        self.client.force_login(self.chef)
        resp = self.client.post(reverse("kitchen:shrinkage", args=[order.pk]), {
            "item_id": item.pk,
            "reason": "producto quemado",
            "notify_waiter_replacement": "on",
        })
        self.assertRedirects(resp, reverse("kitchen:kds"))
        item.refresh_from_db()
        self.assertTrue(item.cancelled_reason)
        self.assertTrue(Shrinkage.objects.filter(order_item=item).exists())
        from audit.models import AuditLog, ActionType
        self.assertTrue(
            AuditLog.objects.filter(action=ActionType.SHRINKAGE, object_id=str(item.pk)).exists()
        )