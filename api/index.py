import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbershop.settings')

import django
django.setup()

try:
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)

    from django.contrib.auth.models import User
    admin_user = os.environ.get('DJANGO_ADMIN_USER', 'admin')
    admin_email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@velvetsteel.ph')
    admin_pass = os.environ.get('DJANGO_ADMIN_PASSWORD', '')
    if admin_pass and not User.objects.filter(username=admin_user).exists():
        User.objects.create_superuser(admin_user, admin_email, admin_pass)
        print(f"Superuser '{admin_user}' created.", file=sys.stderr)
except Exception as e:
    print(f"Startup warning: {e}", file=sys.stderr)

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()