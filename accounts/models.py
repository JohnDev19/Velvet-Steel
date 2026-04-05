from mongoengine import Document, IntField, StringField, DateTimeField, BooleanField, DictField
from django.utils import timezone


class UserProfile(Document):
    user_id        = IntField(required=True, unique=True)
    phone          = StringField(max_length=15)
    address        = StringField(max_length=200)
    city           = StringField(max_length=100, default='Metro Manila')
    photo          = StringField()   # relative path or URL
    loyalty_points = IntField(default=0)
    created_at     = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'accounts_userprofile',
    }

    def __str__(self):
        return f"UserProfile(user_id={self.user_id})"

    @property
    def full_name(self):
        return str(self.user_id)


class MongoUser(Document):
    django_id    = IntField(unique=True)
    username     = StringField(max_length=150, required=True, unique=True)
    email        = StringField(max_length=254, default='')
    password     = StringField(required=True)
    first_name   = StringField(max_length=150, default='')
    last_name    = StringField(max_length=150, default='')
    is_active    = BooleanField(default=True)
    is_staff     = BooleanField(default=False)
    is_superuser = BooleanField(default=False)
    date_joined  = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'auth_mongouser',
        'indexes': ['username', 'email', 'django_id'],
    }

    def __str__(self):
        return f"MongoUser({self.username})"


class EmailVerification(Document):
    email      = StringField(required=True)
    username   = StringField(required=True)
    code       = StringField(required=True)
    attempts   = IntField(default=0)
    expires_at = DateTimeField(required=True)

    meta = {
        'collection': 'email_verifications',
        'indexes': ['email', 'username'],
    }

    def __str__(self):
        return f"EmailVerification({self.email})"


class PasswordResetRequest(Document):
    email      = StringField(required=True)
    code       = StringField(required=True)
    attempts   = IntField(default=0)
    expires_at = DateTimeField(required=True)

    meta = {
        'collection': 'password_reset_requests',
        'indexes': ['email'],
    }

    def __str__(self):
        return f"PasswordResetRequest({self.email})"


class AccountDeletionRequest(Document):
    user_id    = IntField(required=True)
    code       = StringField(required=True)
    attempts   = IntField(default=0)
    expires_at = DateTimeField(required=True)

    meta = {
        'collection': 'account_deletion_requests',
        'indexes': ['user_id'],
    }

    def __str__(self):
        return f"AccountDeletionRequest(user_id={self.user_id})"