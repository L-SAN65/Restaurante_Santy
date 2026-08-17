from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from kitchen.models import Order


class CashRegisterStatus(models.TextChoices):
    OPEN = "OPEN", "Abierta"
    CLOSED = "CLOSED", "Cerrada"
    SQUARED = "SQUARED", "Cuadrada"
    UNRECONCILED = "UNRECONCILED", "Descuadre Pendiente"


class CashRegister(models.Model):
    """Caja por turno (RF-25, RF-26, RF-10, RF-11, RF-09).

    - Una sola apertura activa por caja (invariante).
    - Cierre ciego: no muestra saldo esperado al Cajero.
    - Cuadrada si |diferencia| <= 2,00 USD; si no exige justificación.
    """

    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="opened_registers",
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="closed_registers",
    )
    opening_fund = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        max_length=16,
        choices=CashRegisterStatus.choices,
        default=CashRegisterStatus.OPEN,
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    declared_cash = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    difference = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    justification = models.TextField(blank=True)

    class Meta:
        verbose_name = "Caja"
        verbose_name_plural = "Cajas (turnos)"

    def __str__(self):
        return f"Caja #{self.pk} ({self.operator})"

    @property
    def operator(self):
        return self.opened_by.role

    def close_blind(self, declared_cash):
        """Cierre ciego con tolerancia de descuadre (RF-10/RF-11)."""
        from decimal import Decimal

        expected = self.total_billed
        self.declared_cash = Decimal(str(declared_cash))
        self.difference = abs(self.declared_cash - expected).quantize(Decimal("0.01"))
        self.justification = ""
        self.status = (
            CashRegisterStatus.SQUARED
            if self.difference <= Decimal("2.00")
            else CashRegisterStatus.UNRECONCILED
        )
        self.save(update_fields=["declared_cash", "difference", "justification", "status"])

    @property
    def total_billed(self):
        from django.db.models import Sum

        total = self.invoices.filter(status=InvoiceStatus.ISSUED).aggregate(
            total=Sum("total")
        )["total"]
        return total or 0

    def justify_and_close(self, justification):
        """Completa el cierre tras justificar el descuadre (RF-11)."""
        from django.utils import timezone

        if not justification.strip():
            raise ValueError("La justificación es obligatoria para cerrar con descuadre.")
        self.justification = justification
        self.closed_at = timezone.now()
        self.save(update_fields=["justification", "closed_at"])


class InvoiceStatus(models.TextChoices):
    DRAFT = "DRAFT", "Borrador"
    ISSUED = "ISSUED", "Emitida"
    ANNULLED = "ANNULLED", "Anulada"


class PaymentType(models.TextChoices):
    FULL = "FULL", "Pago completo"
    PARTIAL = "PARTIAL", "Pago parcial"


class Invoice(models.Model):
    """Factura emitida con IVA 15% y redondeo a 2 decimales (RF-07).

    Anulación solo por Administrador, conservando el comprobante (RF-08).
    Cobros parciales liberan la mesa y dejan saldo pendiente (RF-09).
    """

    register = models.ForeignKey(
        CashRegister,
        on_delete=models.PROTECT,
        related_name="invoices",
        null=True,
        blank=True,
    )
    order = models.OneToOneField(
        Order, null=True, blank=True, on_delete=models.PROTECT, related_name="invoice"
    )
    client_name = models.CharField(max_length=180, blank=True)
    client_cedula = models.CharField(max_length=16, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=4, default="0.15")
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(
        max_length=10, choices=PaymentType.choices, default=PaymentType.FULL
    )
    status = models.CharField(
        max_length=16, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT
    )
    issued_at = models.DateTimeField(null=True, blank=True)
    annulled_at = models.DateTimeField(null=True, blank=True)
    annulled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="annulled_invoices",
    )

    class Meta:
        ordering = ["-issued_at"]
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"

    def __str__(self):
        return f"Factura #{self.pk} · {self.total} USD ({self.get_status_display()})"

    @property
    def remaining_balance(self):
        """Saldo pendiente tras pago parcial (RF-09)."""
        from decimal import Decimal

        return (self.total - self.paid_amount).quantize(Decimal("0.01"))

    def issue(self):
        from django.utils import timezone

        self.status = InvoiceStatus.ISSUED
        self.issued_at = timezone.now()
        self.save(update_fields=["status", "issued_at"])

    def can_be_annulled_by(self, user):
        return user.role == "ADMIN" and self.status == InvoiceStatus.ISSUED

    def annul(self, user):
        """RF-08: anulación autorizada, comprobante conservado."""
        if not self.can_be_annulled_by(user):
            raise PermissionError("Solo el Administrador puede anular una factura emitida.")
        from django.utils import timezone

        self.status = InvoiceStatus.ANNULLED
        self.annulled_at = timezone.now()
        self.annulled_by = user
        self.save(update_fields=["status", "annulled_at", "annulled_by"])