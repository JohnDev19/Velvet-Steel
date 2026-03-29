from mongoengine import Document, IntField, StringField, ImageField, DateTimeField, BooleanField
from django.utils import timezone


class UserProfile(Document):
    """
    Stores extended profile data for Django auth users.
    Links via user_id (Django User pk).
    """
    user_id = IntField(required=True, unique=True)
    phone = StringField(max_length=15)
    address = StringField(max_length=200)
    city = StringField(max_length=100, default='Metro Manila')
    photo = StringField()   # store relative path or URL
    loyalty_points = IntField(default=0)
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'accounts_userprofile',
    }

    def __str__(self):
        return f"UserProfile(user_id={self.user_id})"

    @property
    def full_name(self):
        return str(self.user_id)