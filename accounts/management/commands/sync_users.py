import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dotenv import dotenv_values


class Command(BaseCommand):
    help = 'Sync MongoUser records into Django auth_user table.'

    def handle(self, *args, **options):
        try:
            from accounts.models import MongoUser
        except Exception as e:
            self.stderr.write(f'sync_users: cannot import MongoUser — {e}')
            return

        env = dotenv_values('.env')
        admin_username = env.get('DJANGO_ADMIN_USER', os.environ.get('DJANGO_ADMIN_USER', 'admin'))
        admin_email    = env.get('DJANGO_ADMIN_EMAIL', os.environ.get('DJANGO_ADMIN_EMAIL', ''))
        admin_password = env.get('DJANGO_ADMIN_PASSWORD', os.environ.get('DJANGO_ADMIN_PASSWORD', ''))

        synced = 0
        try:
            mongo_users = list(MongoUser.objects.all())
        except Exception as e:
            self.stderr.write(f'sync_users: MongoDB query failed — {e}')
            mongo_users = []

        mongo_ids = {mu.django_id for mu in mongo_users}

        for dj in User.objects.all():
            if dj.pk not in mongo_ids:
                self.stdout.write(f'  Removing orphan Django user: {dj.username} (id={dj.pk})')
                dj.delete()
        for mu in mongo_users:
            try:
                existing = User.objects.filter(pk=mu.django_id).first()
                if existing:
                    existing.username     = mu.username
                    existing.email        = mu.email
                    existing.first_name   = mu.first_name
                    existing.last_name    = mu.last_name
                    existing.password     = mu.password
                    existing.is_active    = mu.is_active
                    existing.is_staff     = mu.is_staff
                    existing.is_superuser = mu.is_superuser
                    existing.save()
                else:
                    u = User(pk=mu.django_id)
                    u.username     = mu.username
                    u.email        = mu.email
                    u.first_name   = mu.first_name
                    u.last_name    = mu.last_name
                    u.password     = mu.password
                    u.is_active    = mu.is_active
                    u.is_staff     = mu.is_staff
                    u.is_superuser = mu.is_superuser
                    try:
                        dj = datetime(
                            mu.date_joined.year, mu.date_joined.month, mu.date_joined.day,
                            mu.date_joined.hour, mu.date_joined.minute, mu.date_joined.second,
                        ) if mu.date_joined else datetime.utcnow()
                        u.date_joined = dj
                    except Exception:
                        pass
                    u.save(force_insert=True)
                synced += 1
            except Exception as e:
                self.stderr.write(f'  Failed to sync {mu.username}: {e}')

        # admin superuser
        if admin_username and admin_password:
            admin = User.objects.filter(username=admin_username).first()
            if not admin:
                admin = User.objects.filter(is_superuser=True).first()
            if admin:
                if not admin.check_password(admin_password):
                    admin.set_password(admin_password)
                    admin.save()
                    # MongoUser hash
                    try:
                        mu_admin = MongoUser.objects(django_id=admin.pk).first()
                        if mu_admin:
                            mu_admin.password = admin.password
                            mu_admin.save()
                    except Exception:
                        pass
            else:
                # fresh admin
                admin = User.objects.create_superuser(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                )
                try:
                    mu_new = MongoUser(
                        django_id=admin.pk,
                        username=admin.username,
                        email=admin.email,
                        password=admin.password,
                        is_active=True,
                        is_staff=True,
                        is_superuser=True,
                    )
                    mu_new.save()
                except Exception:
                    pass

        self.stdout.write(self.style.SUCCESS(f'sync_users: synced {synced} user(s).'))
