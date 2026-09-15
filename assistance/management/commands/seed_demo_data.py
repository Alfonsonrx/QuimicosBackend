import random
from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from assistance.models import AssistanceRecord

User = get_user_model()

DEMO_PASSWORD = "DemoPass123!"

EMPLOYEES = [
    # email, name, first_lastname, second_lastname, position
    ("juan.perez@example.com", "Juan", "Perez", "Diaz", "Bodeguero"),
    ("maria.lopez@example.com", "Maria", "Lopez", None, "Analista"),
    ("carlos.ruiz@example.com", "Carlos", "Ruiz", "Soto", "Chofer"),
    ("ana.torres@example.com", "Ana", "Torres", None, "Recepcionista"),
    ("pedro.sanchez@example.com", "Pedro", "Sanchez", "Vega", None),
]

ADMIN = ("laura.gomez@example.com", "Laura", "Gomez", "Administradora")
SUPERUSER = ("superadmin@example.com", "Super", "Admin")


class Command(BaseCommand):
    help = "Seeds the database with fake users and assistance records for manual API testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--weeks",
            type=int,
            default=3,
            help="How many past business weeks of history to generate (default: 3).",
        )

    def handle(self, *args, **options):
        random.seed(42)
        weeks = options["weeks"]
        today = timezone.localdate()

        with transaction.atomic():
            superuser = self._get_or_create_superuser()
            admin = self._get_or_create_admin()
            employees = [self._get_or_create_employee(*data) for data in EMPLOYEES]
            self._seed_today(employees, admin, today)
            self._seed_history(employees, weeks, today)

        self.stdout.write(self.style.SUCCESS("\nSeed complete. Login credentials (all use the same password):"))
        self.stdout.write(f"  password: {DEMO_PASSWORD}\n")
        self.stdout.write(f"  superuser (Django admin): {superuser.email}")
        self.stdout.write(f"  admin (administrador, for API): {admin.email}")
        for emp in employees:
            self.stdout.write(f"  employee: {emp.email} ({emp.position or 'no position'})")

    def _get_or_create_superuser(self):
        email, name, first_lastname = SUPERUSER
        user, created = User.objects.get_or_create(
            email=email,
            defaults=dict(name=name, first_lastname=first_lastname, type=User.UserType.ADMIN),
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.is_staff = True
            user.is_superuser = True
            user.save()
        elif user.type != User.UserType.ADMIN:
            # Keep it out of employee-facing stats even on re-runs against an older seed.
            user.type = User.UserType.ADMIN
            user.save()
        return user

    def _get_or_create_admin(self):
        email, name, first_lastname, second_lastname = ADMIN
        user, created = User.objects.get_or_create(
            email=email,
            defaults=dict(
                name=name,
                first_lastname=first_lastname,
                second_lastname=second_lastname,
                type=User.UserType.ADMIN,
            ),
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        return user

    def _get_or_create_employee(self, email, name, first_lastname, second_lastname, position):
        user, created = User.objects.get_or_create(
            email=email,
            defaults=dict(
                name=name,
                first_lastname=first_lastname,
                second_lastname=second_lastname,
                position=position,
                type=User.UserType.EMPLEADO,
            ),
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        return user

    def _record_exists(self, user, date, record_type):
        return AssistanceRecord.objects.filter(user=user, date=date, type=record_type).exists()

    def _seed_today(self, employees, admin, today):
        juan, maria, carlos, ana, pedro = employees

        # Juan: on-time ingreso -> present, not delayed
        if not self._record_exists(juan, today, AssistanceRecord.AssistanceType.INGRESO):
            AssistanceRecord.objects.create(
                user=juan, date=today, time=time(8, 5), type=AssistanceRecord.AssistanceType.INGRESO, delay=False
            )

        # Maria: late ingreso -> present, delayed
        if not self._record_exists(maria, today, AssistanceRecord.AssistanceType.INGRESO):
            AssistanceRecord.objects.create(
                user=maria, date=today, time=time(9, 20), type=AssistanceRecord.AssistanceType.INGRESO, delay=True
            )

        # Carlos: anticipated absence pre-registered by the admin -> anticipated_absence
        if not self._record_exists(carlos, today, AssistanceRecord.AssistanceType.FALTA_ANTICIPADA):
            AssistanceRecord.objects.create(
                user=carlos, date=today, time=time(0, 0), type=AssistanceRecord.AssistanceType.FALTA_ANTICIPADA
            )

        # Ana: no record at all today -> absence

        # Pedro: full day, ingreso + salida -> present
        if not self._record_exists(pedro, today, AssistanceRecord.AssistanceType.INGRESO):
            AssistanceRecord.objects.create(
                user=pedro, date=today, time=time(7, 55), type=AssistanceRecord.AssistanceType.INGRESO, delay=False
            )
        if not self._record_exists(pedro, today, AssistanceRecord.AssistanceType.SALIDA):
            AssistanceRecord.objects.create(
                user=pedro, date=today, time=time(17, 0), type=AssistanceRecord.AssistanceType.SALIDA
            )

    def _seed_history(self, employees, weeks, today):
        start = today - timedelta(days=weeks * 7)
        current = start
        while current < today:
            if current.weekday() < 5:  # Mon-Fri only
                for emp in employees:
                    if random.random() < 0.8:  # ~80% attendance rate
                        if not self._record_exists(emp, current, AssistanceRecord.AssistanceType.INGRESO):
                            hour = random.choice([8, 8, 8, 9, 9])
                            minute = random.randint(0, 59)
                            AssistanceRecord.objects.create(
                                user=emp,
                                date=current,
                                time=time(hour, minute),
                                type=AssistanceRecord.AssistanceType.INGRESO,
                                delay=hour >= 9,
                            )
            current += timedelta(days=1)
