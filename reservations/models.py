from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Service(models.Model):
    CATEGORY_CHOICES = [
        ('haircut', 'Haircut'),
        ('shave', 'Shave & Beard'),
        ('treatment', 'Hair Treatment'),
        ('combo', 'Combo Package'),
        ('kids', "Kids' Cut"),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='haircut')
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, default='scissors')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'price']

    def __str__(self):
        return f"{self.name} - ₱{self.price}"


class Barber(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=200)
    bio = models.TextField()
    experience_years = models.IntegerField(default=1)
    photo = models.ImageField(upload_to='barbers/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    instagram = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='time_slots')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.barber.name} - {self.get_day_of_week_display()} {self.start_time}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='reservations')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmation_code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.appointment_date} {self.appointment_time}"

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            import random, string
            self.confirmation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not self.total_price:
            self.total_price = self.service.price
        super().save(*args, **kwargs)


class Testimonial(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    comment = models.TextField()
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.rating}★"


class GalleryImage(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    barber = models.ForeignKey(Barber, on_delete=models.SET_NULL, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
