from datetime import timedelta

from django.conf import settings
from django.db import models

from core.models import BusinessConfig


class TableStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Disponible"
    RESERVED = "RESERVED", "Reservada"
    OCCUPIED = "OCCUPIED", "Ocupada"
    BLOCKED = "BLOCKED", "Bloqueada"


class Room(models.TextChoices):
    VIP = "VIP", "Sala VIP"
    TERRAZA = "TERRAZA", "Terraza"
    PISO_1 = "PISO_1", "Piso 1"


class Table(models.Model):
    """Mesa del restaurante (capacidades soportadas: 2, 4, 6 y 12).

    Salas: VIP, Terraza, Piso 1 (Room). Coordenadas x,y para plano visual.
    """

    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(
        choices=[(2, "2"), (4, "4"), (6, "6"), (12, "12")]
    )
    room = models.CharField(
        max_length=16,
        choices=Room.choices,
        default=Room.PISO_1,
        verbose_name="Sala",
    )
    x = models.FloatField(default=0, help_text="Coordenada X (0-100) para plano visual")
    y = models.FloatField(default=0, help_text="Coordenada Y (0-100) para plano visual")
    shape = models.CharField(max_length=16, default="circle")
    is_contiguous_group = models.CharField(max_length=255, blank=True)
    disabled = models.BooleanField(default=False)

    class Meta:
        ordering = ["number"]
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"

    def __str__(self):
        return f"Mesa {self.number} ({self.capacity} pax)"

    @property
    def status(self):
        from django.utils import timezone

        now = timezone.now()
        if self.disabled:
            return TableStatus.AVAILABLE

        if self.active_blocks.filter(confirmed=False, expires_at__gt=now).exists():
            return TableStatus.BLOCKED

        active = self.reservations.filter(
            status=ReservationStatus.RESERVED,
            start_at__lte=now,
            end_at__gte=now,
        )
        if active.exists():
            return TableStatus.OCCUPIED

        from kitchen.models import OrderStatus

        if self.orders.filter(
            status__in=[OrderStatus.WAITING, OrderStatus.PREPARING, OrderStatus.READY]
        ).exists():
            return TableStatus.OCCUPIED

        upcoming = self.reservations.filter(
            status=ReservationStatus.RESERVED,
            start_at__gt=now,
        )
        if upcoming.exists():
            return TableStatus.RESERVED

        return TableStatus.AVAILABLE


class ReservationStatus(models.TextChoices):
    RESERVED = "RESERVED", "Reservada"
    CONFIRMED = "CONFIRMED", "Confirmada"
    COMPLETED = "COMPLETED", "Completada"
    CANCELLED = "CANCELLED", "Cancelada"
    NO_SHOW = "NO_SHOW", "Cancelada por no-show"


class Reservation(models.Model):
    """Reserva de 2 horas en bloque, mínimo 12h de anticipación (RF-27..29).

    Bloqueo de 2 min evita doble confirmación concurrente (RNF-05).
    Tolerancia de no-show: 15 minutos (RF-04, RF-31).
    Cancelable por el cliente con >= 4 horas de anticipación (RF-33).
    """

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
        null=True,
        blank=True,
    )
    client_email = models.EmailField()
    client_cedula = models.CharField(max_length=16)
    guests = models.PositiveIntegerField(default=1)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(
        max_length=16,
        choices=ReservationStatus.choices,
        default=ReservationStatus.RESERVED,
    )
    tables = models.ManyToManyField(Table, related_name="reservations")
    created_at = models.DateTimeField(auto_now_add=True)
    cancel_notice_hours = models.IntegerField(default=0)

    class Meta:
        ordering = ["start_at"]
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    def __str__(self):
        return f"Reserva {self.client_email} {self.start_at:%d/%m %H:%M}"

    def save(self, *args, **kwargs):
        if not self.end_at or self.end_at <= self.start_at:
            self.end_at = self.start_at + timedelta(hours=2)
        super().save(*args, **kwargs)

    def with_domain_clock(self, now):
        self._now = now
        return self

    def cancel_allowed(self):
        """RF-33: cancelación autónoma solo con >= 4 horas de anticipación."""
        from django.utils import timezone

        now = getattr(self, "_now", None) or timezone.now()
        return (self.start_at - now).total_seconds() >= 4 * 3600

    def register_no_show(self):
        """RF-31: cancelar por inasistencia tras 15 min de gracia."""
        from django.utils import timezone

        config = BusinessConfig.objects.get(pk=1)
        now = getattr(self, "_now", None) or timezone.now()
        if now < self.start_at + timedelta(minutes=config.no_show_grace_minutes):
            raise ValueError("Aún dentro del período de gracia de no-show.")
        self.status = ReservationStatus.NO_SHOW
        self.save(update_fields=["status"])


class TableBlock(models.Model):
    """Bloqueo de 2 minutos sobre mesas seleccionadas (RF-28).

    Persiste aunque el navegador se cierre; impide doble reserva concurrente.
    """

    token = models.CharField(max_length=64, unique=True)
    tables = models.ManyToManyField(Table, related_name="active_blocks")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Bloqueo de mesa"
        verbose_name_plural = "Bloqueos de mesa"

    def __str__(self):
        return f"Bloqueo {self.token} expira {self.expires_at:%H:%M:%S}"

    @property
    def is_active(self):
        from django.utils import timezone

        return not self.confirmed and timezone.now() < self.expires_at