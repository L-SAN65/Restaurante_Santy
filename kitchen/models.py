from datetime import timedelta

from django.conf import settings
from django.db import models


class OrderStatus(models.TextChoices):
    WAITING = "WAITING", "En Espera"
    PREPARING = "PREPARING", "En Preparación"
    READY = "READY", "Listo"
    DELIVERED = "DELIVERED", "Entregado"
    CANCELLED = "CANCELLED", "Cancelada"


class Order(models.Model):
    """Comanda enviada a cocina (RF-20).

    Vida en estado: En Espera -> En Preparación -> Listo/cancelación.
    El semáforo de tiempos se calcula desde started_at (RF-05).
    """

    table = models.ForeignKey(
        "reservations.Table",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    waiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="taken_orders",
    )
    status = models.CharField(
        max_length=16,
        choices=OrderStatus.choices,
        default=OrderStatus.WAITING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Comanda"
        verbose_name_plural = "Comandas"

    def __str__(self):
        return f"Comanda {self.pk} · Mesa {self.table.number}"

    def start_preparation(self):
        from django.utils import timezone

        self.status = OrderStatus.PREPARING
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at"])

    def elapsed_minutes(self, now=None):
        from django.utils import timezone

        if not self.started_at:
            return 0
        now = now or timezone.now()
        return int((now - self.started_at).total_seconds() // 60)

    @property
    def traffic_light(self):
        """RF-05 semáforo: <10 verde, 10-20 amarillo, >20 rojo."""
        minutes = self.elapsed_minutes()
        if minutes < 10:
            return "green"
        if minutes <= 20:
            return "yellow"
        return "red"


class OrderItem(models.Model):
    """Platillo dentro de una comanda (RF-21)."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=180)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.CharField(max_length=255, blank=True)
    is_completed = models.BooleanField(default=False)
    cancelled_reason = models.CharField(max_length=255, blank=True)
    replacement_requested = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Ítem de comanda"
        verbose_name_plural = "Ítems de comanda"

    def __str__(self):
        return f"{self.quantity} × {self.name}"

    @property
    def subtotal(self):
        from decimal import ROUND_HALF_UP, Decimal

        return (self.quantity * self.unit_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )


class Shrinkage(models.Model):
    """Merma registrada por el Chef (RF-06).

    Conserva el cargo original del ítem, crea auditoría y genera
    alerta de reposición a $0.00 si se solicita.
    """

    order_item = models.OneToOneField(
        OrderItem, on_delete=models.PROTECT, related_name="shrinkage"
    )
    reason = models.TextField()
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="shrinkages"
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    notify_waiter_replacement = models.BooleanField(default=False)
    replaced_amount = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")

    class Meta:
        verbose_name = "Merma"
        verbose_name_plural = "Mermas"

    def __str__(self):
        return f"Merma {self.pk} · {self.order_item.name} ({self.registered_at:%Y-%m-%d})"


class Dish(models.Model):
    """Platillo del menú (REF: ficha técnica en módulo inventory)."""

    ACTIVE = "ACTIVE"
    DISABLED_STOCK = "DISABLED_STOCK"

    name = models.CharField(max_length=180)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.CharField(
        max_length=24,
        default=ACTIVE,
    )
    active = models.BooleanField(default=True)
    image = models.ImageField(
        upload_to="dishes/",
        blank=True,
        null=True,
        help_text="Imagen del platillo para el menú cliente (recomendado 800x600, JPG/PNG, máx 2MB).",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Descripción corta para el menú cliente.",
    )

    class Meta:
        verbose_name = "Platillo"
        verbose_name_plural = "Platillos"

    def __str__(self):
        return self.name