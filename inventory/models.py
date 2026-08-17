from django.conf import settings
from django.db import models


class Ingredient(models.Model):
    """Insumo con costo promedio ponderado (RF-23)."""

    name = models.CharField(max_length=180)
    unit = models.CharField(max_length=12)  # kg, g, L, unidades
    current_stock = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    min_stock = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    average_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"

    def __str__(self):
        return f"{self.name} ({self.unit})"

    @property
    def below_minimum(self):
        return self.current_stock < self.min_stock

    def apply_receipt(self, quantity, unit_cost):
        """Recalcula costo promedio ponderado (RF-23)."""
        from decimal import Decimal

        qty = Decimal(str(quantity))
        cost = Decimal(str(unit_cost))
        old_total = self.current_stock * self.average_cost
        new_total = old_total + qty * cost
        self.current_stock += qty
        if self.current_stock > 0:
            self.average_cost = (new_total / self.current_stock).quantize(Decimal("0.01"))
        self.save(update_fields=["current_stock", "average_cost"])


class TechnicalSheet(models.Model):
    """Ficha técnica del platillo: fuente para deducción de stock (RF-13, RF-14)."""

    dish = models.OneToOneField("kitchen.Dish", on_delete=models.CASCADE, related_name="sheet")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ficha técnica"
        verbose_name_plural = "Fichas técnicas"

    def __str__(self):
        return f"Ficha técnica: {self.dish.name}"

    @property
    def can_be_served(self):
        """RF-14: disponible si todos los insumos cubren la cantidad requerida."""
        return all(item.is_satisfied for item in self.ingredients.all())

    def deduct_ingredients(self):
        """Deduce insumos al enviar la comanda (RF-20)."""
        for item in self.ingredients.all():
            item.ingredient.apply_receipt(-1 * item.quantity, 0)


class TechnicalSheetItem(models.Model):
    sheet = models.ForeignKey(TechnicalSheet, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        verbose_name = "Insumo de ficha"
        verbose_name_plural = "Insumos de ficha"

    def __str__(self):
        return f"{self.sheet.dish.name} → {self.ingredient.name} × {self.quantity}"

    @property
    def is_satisfied(self):
        return self.ingredient.current_stock >= self.quantity


class Receipt(models.Model):
    """Recepción de inventario: traza lote, caducidad y costo (RF-23)."""

    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name="receipts")
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="receipts"
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    lot = models.CharField(max_length=64)
    expiry_date = models.DateField(null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Recepción"
        verbose_name_plural = "Recepciones"

    def __str__(self):
        return f"Recepción {self.pk} · {self.ingredient.name} × {self.quantity}"

    def confirm(self):
        """Confirma y aplica stock (RF-23). Recepción confirmada es inmutable."""
        if self.confirmed:
            raise ValueError("La recepción ya fue confirmada.")
        self.ingredient.apply_receipt(self.quantity, self.unit_cost)
        self.confirmed = True
        self.save(update_fields=["confirmed"])


class CorrectionRequestStatus(models.TextChoices):
    PENDING = "PENDING", "Pendiente de Aprobación"
    APPROVED = "APPROVED", "Aprobada"
    REJECTED = "REJECTED", "Rechazada"


class CorrectionRequest(models.Model):
    """Solicitud de corrección de recepción confirmada (RF-24).

    Impide edición directa; requiere aprobación del Administrador,
    registrada en auditoría.
    """

    receipt = models.ForeignKey(Receipt, on_delete=models.PROTECT, related_name="corrections")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="correction_requests"
    )
    difference_quantity = models.DecimalField(max_digits=12, decimal_places=3)
    reason = models.TextField()
    status = models.CharField(
        max_length=16,
        choices=CorrectionRequestStatus.choices,
        default=CorrectionRequestStatus.PENDING,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reviewed_corrections",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Solicitud de corrección"
        verbose_name_plural = "Solicitudes de corrección"

    def __str__(self):
        return f"Corrección #{self.pk} · {self.receipt.ingredient.name}"

    def approve(self, user):
        if self.status != CorrectionRequestStatus.PENDING:
            raise ValueError("Solo se aprueban solicitudes pendientes.")
        self.status = CorrectionRequestStatus.APPROVED
        self.reviewed_by = user
        self.save(update_fields=["status", "reviewed_by"])

    def reject(self, user):
        if self.status != CorrectionRequestStatus.PENDING:
            raise ValueError("Solo se rechazan solicitudes pendientes.")
        self.status = CorrectionRequestStatus.REJECTED
        self.reviewed_by = user
        self.save(update_fields=["status", "reviewed_by"])