from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()


class Command(BaseCommand):
    help = "Seed a default superadmin user (idempotent — safe to re-run on every deploy)"

    def handle(self, *args, **options):
        username = config("SUPERADMIN_USERNAME", default="md")
        password = config("SUPERADMIN_PASSWORD", default="password")
        email = config("SUPERADMIN_EMAIL", default="admin@sirlewizz.com")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
                "role": User.Role.ADMIN,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"✅ Superadmin '{username}' created successfully.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"ℹ️  Superadmin '{username}' already exists — skipped.")
            )
