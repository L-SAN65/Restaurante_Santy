from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import BusinessConfig, Role, User
from reservations.models import Reservation, ReservationStatus, Table, TableBlock


class ReservationsViewTest(TestCase):
    def setUp(self):
        config, _ = BusinessConfig.objects.get_or_create(pk=1)
        config.no_show_grace_minutes = 15
        config.save()
        self.waiter = User.objects.create_user(
            username="waiter@test.com", password="pass", role=Role.WAITER
        )
        self.client_user = User.objects.create_user(
            username="cliente@test.com",
            password="pass",
            role=Role.CLIENT,
            cedula="8-123-456",
        )
        self.table = Table.objects.create(number=1, capacity=4)
        self.table2 = Table.objects.create(number=2, capacity=4)

    def _make_reservation(self, start_at=None):
        start = start_at or timezone.now() + timedelta(days=1)
        res = Reservation.objects.create(
            client=self.client_user,
            client_email=self.client_user.email,
            client_cedula=self.client_user.cedula,
            guests=4,
            start_at=start,
            status=ReservationStatus.RESERVED,
        )
        res.tables.add(self.table)
        return res

    def test_floor_plan_200_for_waiter(self):
        self.client.force_login(self.waiter)
        resp = self.client.get(reverse("reservations:floor_plan"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Mesa 1")

    def test_checkin_updates_guests_and_joins_tables(self):
        reservation = self._make_reservation()
        self.client.force_login(self.waiter)
        resp = self.client.post(reverse("reservations:checkin"), {
            "reservation_id": reservation.pk,
            "real_people": 6,
            "tables": [self.table2.pk],
        })
        self.assertRedirects(resp, reverse("reservations:checkin"))
        reservation.refresh_from_db()
        self.assertEqual(reservation.guests, 6)
        self.assertEqual(reservation.status, ReservationStatus.CONFIRMED)
        self.assertEqual(reservation.tables.count(), 2)

    def test_no_show_before_grace_denied(self):
        reservation = self._make_reservation(start_at=timezone.now() + timedelta(minutes=5))
        self.client.force_login(self.waiter)
        resp = self.client.post(reverse("reservations:no_show"), {
            "reservation_id": reservation.pk,
        })
        self.assertRedirects(resp, reverse("reservations:checkin"))
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, ReservationStatus.RESERVED)

    def test_no_show_after_grace_succeeds(self):
        start = timezone.now() - timedelta(minutes=16)
        reservation = self._make_reservation(start_at=start)
        self.client.force_login(self.waiter)
        resp = self.client.post(reverse("reservations:no_show"), {
            "reservation_id": reservation.pk,
        })
        self.assertRedirects(resp, reverse("reservations:checkin"))
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, ReservationStatus.NO_SHOW)

    def test_portal_creates_reservation(self):
        self.client.force_login(self.client_user)
        future = timezone.localtime() + timedelta(hours=13)
        resp = self.client.post(reverse("reservations:portal"), {
            "email": "cliente@test.com",
            "cedula": "8-123-456",
            "date": future.strftime("%Y-%m-%d"),
            "time": future.strftime("%H:%M"),
            "guests": "4",
            "tables": [self.table.pk],
        })
        self.assertRedirects(resp, reverse("reservations:my_reservations"))
        self.assertTrue(Reservation.objects.filter(client_cedula="8-123-456").exists())

    def test_portal_rejects_less_than_12h(self):
        self.client.force_login(self.client_user)
        future = timezone.localtime() + timedelta(hours=10)
        resp = self.client.post(reverse("reservations:portal"), {
            "email": "cliente@test.com",
            "cedula": "8-123-456",
            "date": future.strftime("%Y-%m-%d"),
            "time": future.strftime("%H:%M"),
            "guests": "4",
            "tables": [self.table.pk],
        })
        self.assertFalse(Reservation.objects.filter(client_cedula="8-123-456").exists())