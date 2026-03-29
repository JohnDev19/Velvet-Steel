from django.urls import path
from . import admin_views

urlpatterns = [
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    path('reservations/', admin_views.admin_reservations, name='admin_reservations'),
    path('reservations/<str:pk>/update/', admin_views.admin_update_reservation, name='admin_update_reservation'),
    path('barbers/', admin_views.admin_barbers, name='admin_barbers'),
    path('barbers/add/', admin_views.admin_barber_add, name='admin_barber_add'),
    path('barbers/<str:pk>/edit/', admin_views.admin_barber_edit, name='admin_barber_edit'),
    path('barbers/<str:pk>/delete/', admin_views.admin_barber_delete, name='admin_barber_delete'),
    path('testimonials/', admin_views.admin_testimonials, name='admin_testimonials'),
    path('testimonials/<str:pk>/approve/', admin_views.approve_testimonial, name='approve_testimonial'),
    path('analytics/', admin_views.admin_analytics, name='admin_analytics'),
    path('haircut-styles/', admin_views.admin_haircut_styles, name='admin_haircut_styles'),
    path('haircut-styles/add/', admin_views.admin_haircut_style_add, name='admin_haircut_style_add'),
    path('haircut-styles/<str:pk>/edit/', admin_views.admin_haircut_style_edit, name='admin_haircut_style_edit'),
    path('haircut-styles/<str:pk>/delete/', admin_views.admin_haircut_style_delete, name='admin_haircut_style_delete'),
]