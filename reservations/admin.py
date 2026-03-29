from django.contrib import admin
from .models import Service, Barber, Reservation, Testimonial, GalleryImage, TimeSlot, HaircutStyle

admin.site.register(Service)
admin.site.register(Barber)
admin.site.register(Reservation)
admin.site.register(Testimonial)
admin.site.register(GalleryImage)
admin.site.register(TimeSlot)
admin.site.register(HaircutStyle)
