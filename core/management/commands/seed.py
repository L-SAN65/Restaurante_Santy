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

        # Mesas de ejemplo en 3 salas con coordenadas para el plano visual
        from reservations.models import Table

        mesas_iniciales = [
            # Sala VIP — mesas más exclusivas
            (1, 2, "VIP", 15, 30, "circle"),
            (2, 4, "VIP", 50, 25, "circle"),
            (3, 6, "VIP", 80, 30, "circle"),
            (4, 12, "VIP", 50, 70, "circle"),
            # Terraza
            (5, 2, "TERRAZA", 20, 35, "circle"),
            (6, 4, "TERRAZA", 55, 30, "circle"),
            (7, 6, "TERRAZA", 80, 55, "circle"),
            (8, 4, "TERRAZA", 25, 75, "circle"),
            # Piso 1 — salón principal
            (9, 2, "PISO_1", 15, 25, "circle"),
            (10, 4, "PISO_1", 45, 25, "circle"),
            (11, 6, "PISO_1", 75, 25, "circle"),
            (12, 4, "PISO_1", 15, 70, "circle"),
            (13, 6, "PISO_1", 45, 70, "circle"),
            (14, 12, "PISO_1", 75, 70, "circle"),
        ]
        created_count = 0
        for number, cap, room, x, y, shape in mesas_iniciales:
            _, created = Table.objects.get_or_create(
                number=number,
                defaults={"capacity": cap, "room": room, "x": x, "y": y, "shape": shape},
            )
            if created:
                created_count += 1
            else:
                # asegurar sala/coords en mesas preexistentes sin room
                t = Table.objects.get(number=number)
                updated = False
                if not t.room:
                    t.room = room
                    updated = True
                if t.x == 0 and t.y == 0:
                    t.x = x
                    t.y = y
                    updated = True
                if updated:
                    t.save(update_fields=["room", "x", "y"] if t.x else ["room"])
        if created_count:
            self.stdout.write(self.style.SUCCESS(f"{created_count} mesas nuevas creadas. Total: {Table.objects.count()} en 3 salas (VIP/Terraza/Piso 1)."))
        else:
            self.stdout.write(f"Mesas existentes: {Table.objects.count()} (3 salas configuradas).")

        self.stdout.write(self.style.SUCCESS("Seed completado."))