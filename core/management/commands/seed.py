from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import BusinessConfig, Role, User


class Command(BaseCommand):
    help = "Crea datos iniciales: configuración de negocio y usuarios por rol."

    @transaction.atomic
    def handle(self, *args, **options):
        config, created = BusinessConfig.objects.get_or_create(
            pk=1,
            defaults={
                "vat_rate": "0.15",
                "operating_timezone": "America/Panama",
                "operating_start": "10:00",
                "operating_end": "00:00",
                "min_reservation_hours": 12,
                "table_block_minutes": 2,
                "no_show_grace_minutes": 15,
                "cash_tolerance": "2.00",
                "pin_ttl_seconds": 60,
                "loyalty_valid_months": 3,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Configuración de negocio creada."))

        users = {
            "admin@santy.com": ("admin", Role.ADMIN, True),
            "cajero@santy.com": ("cajero", Role.CASHIER, False),
            "mesero@santy.com": ("mesero", Role.WAITER, False),
            "chef@santy.com": ("chef", Role.CHEF, False),
            "bodega@santy.com": ("bodega", Role.WAREHOUSE, False),
        }

        for email, (password, role, staff) in users.items():
            if not User.objects.filter(username=email).exists():
                User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    role=role,
                    first_name=role.capitalize(),
                    is_staff=staff,
                )
                self.stdout.write(f"Usuario {email} creado ({role}).")
            else:
                self.stdout.write(f"Usuario {email} ya existe.")

        self.stdout.write(self.style.SUCCESS("Seed completado."))