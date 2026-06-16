from django.contrib.auth.management.commands import createsuperuser


class Command(createsuperuser.Command):
    help = 'Create a superuser with a password non-interactively'

    def handle(self, *args, **options):
        options.setdefault('interactive', False)
        username = options.get('username') or 'AdminMpha'
        email = options.get('email') or 'mkamkuza@legalaidbureau.org'
        password = options.get('password') or 'Mpha@0019'

        from django.contrib.auth import get_user_model
        User = get_user_model()

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_superuser(username=username, email=email, password=password)
            user.role = 'it_admin'
            user.is_first_login = False
            user.save()
            self.stdout.write(f'Superuser "{username}" created successfully with role it_admin.')
        else:
            user = User.objects.get(username=username)
            user.role = 'it_admin'
            user.is_first_login = False
            user.save()
            self.stdout.write(f'Superuser "{username}" already exists. Role updated to it_admin.')