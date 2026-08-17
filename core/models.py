from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    CASHIER = "CASHIER", "Cajero"
    WAITER = "WAITER", "Mesero"
    CHEF = "CHEF", "Chef"
    WAREHOUSE = "WAREHOUSE", "Encargado de Bodega"
    CLIENT = "CLIENT", "Cliente"


class User(AbstractUser):
    """Usuario del sistema con rol de negocio y control de acceso por intentos.

    Invariantes (BDD):
    - Suspendida: bloqueada 15 min tras 3 fallos consecutivos.
    - Bloqueada: permanente al acumular 5 fallos.
    - Credenciales nunca en texto plano (hash con salt de Django).
    """

    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.WAITER,
    )
    cedula = models.CharField(max_length=16, blank=True, unique=True, null=True)
    failed_login_count = models.IntegerField(default=0)
    suspended_until = models.DateTimeField(null=True, blank=True)
    is_permanently_locked = models.BooleanField(default=False)

    username = models.EmailField(unique=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    def login_allowed(self, now=None):
        """Determina si el usuario puede intentar autenticarse ahora."""
        from django.utils import timezone

        now = now or timezone.now()
        if self.is_permanently_locked:
            return False, "Cuenta bloqueada. Contacte al administrador."
        if self.suspended_until and now < self.suspended_until:
            remaining = (self.suspended_until - now).total_seconds() / 60
            return False, f"Cuenta suspendida. Intente en {remaining:.0f} minutos."
        return True, ""

    def record_failed_login(self, now=None):
        from django.utils import timezone
        from datetime import timedelta

        now = now or timezone.now()
        self.failed_login_count += 1

        if self.failed_login_count >= 5:
            self.is_permanently_locked = True
            self.suspended_until = None
        elif self.failed_login_count >= 3:
            self.suspended_until = now + timedelta(minutes=15)
        self.save(update_fields=[
            "failed_login_count",
            "suspended_until",
            "is_permanently_locked",
        ])

    def reset_login_attempts(self):
        self.failed_login_count = 0
        self.suspended_until = None
        self.is_permanently_locked = False
        self.save(update_fields=[
            "failed_login_count",
            "suspended_until",
            "is_permanently_locked",
        ])

    @property
    def dashboard_url(self):
        mapping = {
            Role.ADMIN: "core:admin_dashboard",
            Role.CASHIER: "core:cashier_dashboard",
            Role.WAITER: "core:waiter_dashboard",
            Role.CHEF: "core:chef_dashboard",
            Role.WAREHOUSE: "core:warehouse_dashboard",
            Role.CLIENT: "reservations:portal",
        }
        return mapping.get(self.role, "core:login")


class BusinessConfig(models.Model):
    """Parámetros de negocio invariantes (BDD), editables por Administrador."""

    name = "Santy"

    vat_rate = models.DecimalField(max_digits=5, decimal_places=4, default="0.15")
    operating_timezone = models.CharField(max_length=64, default="America/Panama")
    operating_start = models.TimeField(default="10:00")
    operating_end = models.TimeField(default="00:00")
    min_reservation_hours = models.IntegerField(default=12)
    table_block_minutes = models.IntegerField(default=2)
    no_show_grace_minutes = models.IntegerField(default=15)
    cash_tolerance = models.DecimalField(max_digits=8, decimal_places=2, default="2.00")
    pin_ttl_seconds = models.IntegerField(default=60)
    loyalty_valid_months = models.IntegerField(default=3)
    points_per_dollar = models.IntegerField(default=1)
    redeem_points_per_dollar = models.IntegerField(default=10)

    class Meta:
        verbose_name = "Configuración de negocio"
        verbose_name_plural = "Configuración de negocio"

    def __str__(self):
        return "Configuración global de Santy"


def get_business_config():
    config, _ = BusinessConfig.objects.get_or_create(pk=1)
    return config