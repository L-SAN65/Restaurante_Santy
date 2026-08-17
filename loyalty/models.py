from datetime import date, timedelta

from django.conf import settings
from django.db import models

from core.models import BusinessConfig


def add_months(value, months):
    """Suma meses a un datetime conservando el día (caducidad RF-17)."""
    month = value.month - 1 + months
    year = value.year + month // 12
    month = month % 12 + 1
    day = min(value.day, __import__("calendar").monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


class MovementType(models.TextChoices):
    ACCRUAL = "ACCRUAL", "Acreditación"
    REDEMPTION = "REDEMPTION", "Canje"
    EXPIRY = "EXPIRY", "Caducidad"


class LoyaltyMovement(models.Model):
    """Movimiento de puntos por cédula (RF-15, RF-16, RF-17).

    - 1 punto por cada USD entero consumido (parte entera).
    - Canje: 10 puntos = 1,00 USD de descuento al subtotal.
    - Caducidad automática a los 3 meses exactos.
    """

    client_cedula = models.CharField(max_length=16, db_index=True)
    client_wallet = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="loyalty_movements",
    )
    movement_type = models.CharField(max_length=12, choices=MovementType.choices)
    points = models.IntegerField()
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Movimiento de puntos"
        verbose_name_plural = "Movimientos de fidelización"

    def __str__(self):
        return f"{self.get_movement_type_display()} {self.points:+d} pts · {self.client_cedula}"

    @classmethod
    def balance(cls, cedula):
        """Saldo vigente (no caducado) de una cédula."""
        from django.utils import timezone

        return cls.objects.filter(client_cedula=cedula).aggregate(
            total=models.Sum("points")
        )["total"] or 0

    @classmethod
    def accrue_for_invoice(cls, invoice):
        """RF-15: acredita parte entera de 1$ = 1 punto tras factura Emitida."""
        from decimal import ROUND_DOWN

        config = BusinessConfig.objects.get(pk=1)
        if not invoice.client_cedula:
            return None
        points = int(invoice.total.quantize(0, rounding=ROUND_DOWN))
        if points <= 0:
            return None
        return cls.objects.create(
            client_cedula=invoice.client_cedula,
            movement_type=MovementType.ACCRUAL,
            points=points,
            expires_at=add_months(invoice.issued_at, config.loyalty_valid_months)
            if invoice.issued_at
            else None,
            reference=f"Factura #{invoice.pk}",
        )

    @classmethod
    def redeem(cls, cedula, points, invoice_subtotal):
        """RF-16: canjea puntos vigentes con descuento al subtotal.

        Retorna el descuento aplicado en USD. Valida saldo suficiente.
        """
        balance = cls.balance(cedula)
        if points > balance:
            raise ValueError("Saldo de puntos insuficiente.")
        if points % 10:
            raise ValueError("El canje debe ser en bloques de 10 puntos.")

        config = BusinessConfig.objects.get(pk=1)
        discount = (points // config.redeem_points_per_dollar)
        if discount > invoice_subtotal:
            raise ValueError("El descuento no puede superar el subtotal.")

        cls.objects.create(
            client_cedula=cedula,
            movement_type=MovementType.REDEMPTION,
            points=-points,
            reference="Canje en facturación",
        )
        return discount

    @classmethod
    def expire_overdue(cls, now=None):
        """RF-17: descuenta puntos cuya fecha de vencimiento venció."""
        from django.utils import timezone

        now = now or timezone.now()
        expired = cls.objects.filter(
            expires_at__lt=now,
            movement_type=MovementType.ACCRUAL,
            points__gt=0,
        )
        count = expired.count()
        expired.update(points=0, movement_type=MovementType.EXPIRY)
        return count