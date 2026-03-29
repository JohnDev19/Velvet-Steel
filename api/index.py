import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbershop.settings')

from django.core.wsgi import get_wsgi_application

import django
django.setup()

from django.db import connection
try:
    connection.ensure_connection()
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)

    from django.contrib.auth.models import User
    admin_user = os.environ.get('DJANGO_ADMIN_USER', 'admin')
    admin_email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@velvetsteel.ph')
    admin_pass = os.environ.get('DJANGO_ADMIN_PASSWORD', '')
    if admin_pass and not User.objects.filter(username=admin_user).exists():
        User.objects.create_superuser(admin_user, admin_email, admin_pass)

except Exception as e:
    import sys
    print(f"Startup warning: {e}", file=sys.stderr)

app = get_wsgi_application()