from mongoengine import (
    Document,
    StringField, IntField, DecimalField, BooleanField,
    DateTimeField,
    ReferenceField,
    CASCADE,
)
from django.utils import timezone
import datetime
import random
import string


class Service(Document):
    CATEGORY_CHOICES = (
        ('haircut', 'Haircut'),
        ('shave', 'Shave & Beard'),
        ('treatment', 'Hair Treatment'),
        ('combo', 'Combo Package'),
        ('kids', "Kids' Cut"),
    )

    name = StringField(max_length=100, required=True)
    category = StringField(max_length=20, choices=CATEGORY_CHOICES, default='haircut')
    description = StringField()
    price = DecimalField(precision=2)
    duration_minutes = IntField(default=30)
    is_active = BooleanField(default=True)
    icon = StringField(max_length=50, default='scissors')
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'reservations_service',
        'ordering': ['category', 'price'],
    }

    def __str__(self):
        return f"{self.name} - ₱{self.price}"

    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)


class Barber(Document):
    name = StringField(max_length=100, required=True)
    specialty = StringField(max_length=200)
    bio = StringField()
    experience_years = IntField(default=1)
    photo = StringField()
    is_active = BooleanField(default=True)
    rating = DecimalField(precision=1, default=5.0)
    instagram = StringField(max_length=100)
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'reservations_barber',
        'ordering': ['name'],
    }

    def __str__(self):
        return self.name


class Reservation(Document):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )

    customer_id = IntField(required=True)
    customer_username = StringField(max_length=150)
    customer_name = StringField(max_length=200)

    barber = ReferenceField(Barber, reverse_delete_rule=CASCADE)
    service = ReferenceField(Service, reverse_delete_rule=CASCADE, null=True)

    appointment_date = StringField()
    appointment_time = StringField()
    status = StringField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = StringField()
    total_price = DecimalField(precision=2)
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)
    confirmation_code = StringField(max_length=10, unique=True)

    meta = {
        'collection': 'reservations_reservation',
        'ordering': ['-appointment_date', '-appointment_time'],
    }

    def __str__(self):
        return f"{self.customer_name} - {self.appointment_date} {self.appointment_time}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def appointment_date_obj(self):
        try:
            return datetime.date.fromisoformat(self.appointment_date)
        except Exception:
            return None

    @property
    def appointment_time_obj(self):
        try:
            return datetime.time.fromisoformat(self.appointment_time)
        except Exception:
            return None

    @property
    def appointment_date_display(self):
        try:
            d = datetime.date.fromisoformat(self.appointment_date)
            return d.strftime('%B %d, %Y')
        except Exception:
            return self.appointment_date or '—'

    @property
    def appointment_time_display(self):
        """Returns a 12-hour formatted time string safe for templates."""
        try:
            t = datetime.time.fromisoformat(self.appointment_time)
            return t.strftime('%I:%M %p')
        except Exception:
            return self.appointment_time or '—'

    @property
    def appointment_month(self):
        try:
            return datetime.date.fromisoformat(self.appointment_date).strftime('%b')
        except Exception:
            return ''

    @property
    def appointment_day(self):
        try:
            return datetime.date.fromisoformat(self.appointment_date).strftime('%d')
        except Exception:
            return ''

    @property
    def appointment_year(self):
        try:
            return datetime.date.fromisoformat(self.appointment_date).strftime('%Y')
        except Exception:
            return ''

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            self.confirmation_code = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
        if self.total_price is None and self.service:
            try:
                self.total_price = self.service.price
            except Exception:
                self.total_price = 0
        if self.total_price is None:
            self.total_price = 0
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class Testimonial(Document):
    customer_id = IntField(null=True)
    customer_name = StringField(max_length=100)
    rating = IntField(min_value=1, max_value=5, default=5)
    comment = StringField()
    service = ReferenceField(Service, null=True)
    is_approved = BooleanField(default=False)
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'reservations_testimonial',
        'ordering': ['-created_at'],
    }

    def __str__(self):
        return f"{self.customer_name} - {self.rating}★"


class GalleryImage(Document):
    title = StringField(max_length=100)
    image = StringField()
    barber = ReferenceField(Barber, null=True)
    is_featured = BooleanField(default=False)
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'reservations_galleryimage',
        'ordering': ['-created_at'],
    }

    def __str__(self):
        return self.title


class HaircutStyle(Document):
    CATEGORY_CHOICES = (
        ('basic',   '₱70–₱100 · Traditional, basic cut'),
        ('finish',  '₱100–₱200 · Cleaner finish'),
        ('styled',  '₱200–₱350 · Styled cuts'),
        ('fade',    '₱350–₱600 · Advanced fades & shaping'),
        ('premium', '₱600–₱1,000+ · Premium full service'),
    )

    name = StringField(max_length=120, required=True)
    category = StringField(max_length=30, choices=CATEGORY_CHOICES)
    description = StringField()
    price = DecimalField(precision=2)
    image = StringField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'reservations_haircutstyle',
        'ordering': ['category', 'price'],
    }

    def __str__(self):
        return f"{self.get_category_display()} – {self.name}"

    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)