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
    image = StringField()
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

    appointment_date = StringField()   # stored as "YYYY-MM-DD" string
    appointment_time = StringField()   # stored as "HH:MM" string
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
    def appointment_date_display(self):
        try:
            return datetime.date.fromisoformat(self.appointment_date).strftime('%B %d, %Y')
        except Exception:
            return self.appointment_date or '—'

    @property
    def appointment_time_display(self):
        try:
            return datetime.time.fromisoformat(self.appointment_time).strftime('%I:%M %p')
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

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            self.confirmation_code = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
        if self.total_price is None:
            try:
                self.total_price = self.service.price if self.service else 0
            except Exception:
                self.total_price = 0
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class Testimonial(Document):
    customer_id = IntField(null=True)
    customer_username = StringField(max_length=150)
    customer_name = StringField(max_length=100)
    reservation_id = StringField(max_length=50)
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

class AboutPage(Document):
    # Shop image
    shop_image       = StringField()

    # Hero / badge
    established_year = StringField(default='2010')

    # Stats row
    stat_years       = StringField(default='15+')
    stat_clients     = StringField(default='5K+')
    stat_barbers     = StringField(default='8+')

    # Story text
    story_lead       = StringField(default='Founded in 2010 by master barber Rico Villanueva in the heart of Quezon City, Velvet Steel was built on a single conviction: that Filipino men deserve a genuinely premium grooming experience.')
    story_body_1     = StringField(default='What started as a small, humble shop on Rizal Avenue has grown into Metro Manila\'s most respected premium barbershop — a place where tradition meets modernity, and where every client is treated like royalty.')
    story_body_2     = StringField(default='We believe that a great haircut is more than just a trim — it\'s an expression of identity, a confidence booster, and a moment of self-care that every man deserves. That\'s why we pour passion, precision, and artistry into every single appointment.')

    # checklist
    value_1          = StringField(default='Certified Master Barbers')
    value_2          = StringField(default='Premium Imported Products')
    value_3          = StringField(default='Strict Hygiene Standards')
    value_4          = StringField(default='100% Filipino-Owned Business')

    # Contact
    address          = StringField(default='123 Rizal Avenue, Quezon City, Metro Manila, Philippines 1100')
    phone_1          = StringField(default='+63 912 345 6789')
    phone_2          = StringField(default='+63 2 8123 4567')
    email_1          = StringField(default='info@velvetsteel.ph')
    email_2          = StringField(default='bookings@velvetsteel.ph')
    hours_weekday    = StringField(default='Mon–Sat: 8:00 AM – 8:00 PM')
    hours_sunday     = StringField(default='Sunday: 9:00 AM – 6:00 PM')

    updated_at       = DateTimeField(default=timezone.now)

    meta = {'collection': 'about_page_content'}

    @classmethod
    def get_singleton(cls):
        obj = cls.objects().first()
        return obj  # None

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
