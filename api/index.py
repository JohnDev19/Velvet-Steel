import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbershop.settings')

import django
django.setup()

_setup_done = False


def sync_users_from_mongo():
    try:
        from accounts.models import MongoUser
        from django.contrib.auth.models import User

        restored = 0
        for mu in MongoUser.objects.all():
            try:
                if User.objects.filter(pk=mu.django_id).exists():
                    continue
                user = User(pk=mu.django_id)
                user.username     = mu.username
                user.email        = mu.email
                user.first_name   = mu.first_name
                user.last_name    = mu.last_name
                user.password     = mu.password
                user.is_active    = mu.is_active
                user.is_staff     = mu.is_staff
                user.is_superuser = mu.is_superuser
                user.date_joined  = mu.date_joined
                user.save(force_insert=True)
                restored += 1
            except Exception as e:
                print(f"Warning: could not restore user '{mu.username}': {e}", file=sys.stderr)

        if restored:
            print(f"INFO: Restored {restored} user(s) from MongoDB.", file=sys.stderr)
    except Exception as e:
        print(f"Warning: sync_users_from_mongo failed: {e}", file=sys.stderr)


def _run_setup():
    global _setup_done
    if _setup_done:
        return
    try:
        from django.core.management import call_command

        call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)

        sync_users_from_mongo()

        call_command('collectstatic', '--noinput', verbosity=0)

        from django.contrib.auth.models import User
        admin_user  = os.environ.get('DJANGO_ADMIN_USER',  'admin')
        admin_email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@velvetsteel.ph')
        admin_pass  = os.environ.get('DJANGO_ADMIN_PASSWORD', '')
        if admin_pass and not User.objects.filter(username=admin_user).exists():
            dj_user = User.objects.create_superuser(admin_user, admin_email, admin_pass)
            _persist_user_to_mongo(dj_user)
            print(f"Superuser '{admin_user}' created.", file=sys.stderr)

        _setup_done = True
    except Exception as e:
        print(f"Startup warning: {e}", file=sys.stderr)


def _persist_user_to_mongo(dj_user):
    try:
        from accounts.models import MongoUser
        mu = MongoUser.objects(username=dj_user.username).first()
        if mu is None:
            mu = MongoUser(username=dj_user.username)
        mu.django_id    = dj_user.pk
        mu.email        = dj_user.email
        mu.first_name   = dj_user.first_name
        mu.last_name    = dj_user.last_name
        mu.password     = dj_user.password
        mu.is_active    = dj_user.is_active
        mu.is_staff     = dj_user.is_staff
        mu.is_superuser = dj_user.is_superuser
        mu.date_joined  = dj_user.date_joined
        mu.save()
    except Exception as e:
        print(f"Warning: could not persist user '{dj_user.username}' to MongoDB: {e}", file=sys.stderr)


_run_setup()

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()