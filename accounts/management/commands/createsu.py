import os

from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import CommandError


class Command(createsuperuser.Command):
    help = (
        'Create (or update) an IT Admin superuser non-interactively, '
        'reading credentials from environment variables so nothing '
        'sensitive is stored in the codebase.\n\n'
        'Required env vars: SUPERUSER_USERNAME, SUPERUSER_EMAIL, '
        'SUPERUSER_PASSWORD'
    )

    def handle(self, *args, **options):
        username = os.environ.get('SUPERUSER_USERNAME')
        email = os.environ.get('SUPERUSER_EMAIL')
        password = os.environ.get('SUPERUSER_PASSWORD')

        if not username or not email or not password:
            raise CommandError(
                'Missing environment variables. Please set '
                'SUPERUSER_USERNAME, SUPERUSER_EMAIL and SUPERUSER_PASSWORD '
                'before running this command.'
            )

        User = get_user_model()

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_superuser(
                username=username, email=email, password=password
            )
            user.role = 'it_admin'
            user.is_first_login = False
            user.save()
            self.stdout.write(
                f'Superuser "{username}" created successfully with role it_admin.'
            )
        else:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.role = 'it_admin'
            user.is_first_login = False
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(
                f'Superuser "{username}" already existed — password and role refreshed.'
            )
