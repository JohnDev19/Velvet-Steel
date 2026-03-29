from django.urls import path
from . import admin_views

urlpatterns = [
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    path('reservations/', admin_views.admin_reservations, name='admin_reservations'),
    path('reservations/<int:pk>/update/', admin_views.admin_update_reservation, name='admin_update_reservation'),
    path('services/', admin_views.admin_services, name='admin_services'),
    path('barbers/', admin_views.admin_barbers, name='admin_barbers'),
    path('testimonials/', admin_views.admin_testimonials, name='admin_testimonials'),
    path('testimonials/<int:pk>/approve/', admin_views.approve_testimonial, name='approve_testimonial'),
    path('analytics/', admin_views.admin_analytics, name='admin_analytics'),
]
