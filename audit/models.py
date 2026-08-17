from django.conf import settings
from django.db import models


class ActionType(models.TextChoices):
    LOGIN = "LOGIN", "Login"
    LOGIN_FAILED = "LOGIN_FAILED", "Login fallido"
    LOGOUT = "LOGOUT", "Logout"
    ANULATION = "ANULATION", "Anulación de factura"
    SHRINKAGE = "SHRINKAGE", "Merma"
    CASH_CLOSE = "CASH_CLOSE", "Cierre de caja"
    CASH_OPEN = "CASH_OPEN", "Apertura de caja"
    PIN_ISSUE = "PIN_ISSUE", "Emisión de PIN"
    PIN_CONSUMED = "PIN_CONSUMED", "PIN consumido"
    INVENTORY_CORRECTION = "INVENTORY_CORRECTION", "Corrección de inventario"
    RESERVATION = "RESERVATION", "Reserva"
    RESERVATION_CANCEL = "RESERVATION_CANCEL", "Cancelación de reserva"
    CHECK_IN = "CHECK_IN", "Check-in"
    NO_SHOW = "NO_SHOW", "No-show"


class Result(models.TextChoices):
    SUCCESS = "SUCCESS", "Éxito"
    FAILURE = "FAILURE", "Fallo"


class AuditLog(models.Model):
    """Bitácora inmutable de operaciones críticas (RF-35, RNF-08).

    Los perfiles operativos no pueden modificar estos registros;
    se protege a nivel de modelo/permiso en servidor.
    """

    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_entries",
    )
    action = models.CharField(max_length=32, choices=ActionType.choices)
    result = models.CharField(max_length=16, choices=Result.choices, default=Result.SUCCESS)
    object_type = models.CharField(max_length=64, blank=True)
    object_id = models.CharField(max_length=255, blank=True)
    detail = models.TextField(blank=True)

    class Meta:
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Bitácora de auditoría"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.user} {self.action}"

    @classmethod
    def log(cls, user, action, result=Result.SUCCESS, object_type="", object_id="", detail=""):
        return cls.objects.create(
            user=user,
            action=action,
            result=result,
            object_type=object_type,
            object_id=object_id,
            detail=detail,
        )


class PinToken(models.Model):
    """PIN de autorización remota de un solo uso (RF-18, RF-19).

    Vigencia de 60 segundos; se invalida al consumirse.
    """

    code = models.CharField(max_length=6)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="issued_pins",
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    action = models.CharField(max_length=64, blank=True)

    class Meta:
        verbose_name = "Token PIN"
        verbose_name_plural = "Tokens PIN"

    def __str__(self):
        return f"PIN {self.code} (expira {self.valid_until:%H:%M:%S})"

    @property
    def is_valid(self):
        from django.utils import timezone

        if self.consumed_at is not None:
            return False
        return timezone.now() < self.valid_until