from django.urls import path
from . import admin_views
from .views import get_available_slots

urlpatterns = [
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    path('reservations/', admin_views.admin_reservations, name='admin_reservations'),
    path('reservations/bulk-delete/', admin_views.admin_bulk_delete_reservations, name='admin_bulk_delete_reservations'),
    path('reservations/<str:pk>/update/', admin_views.admin_update_reservation, name='admin_update_reservation'),
    path('barbers/', admin_views.admin_barbers, name='admin_barbers'),
    path('barbers/add/', admin_views.admin_barber_add, name='admin_barber_add'),
    path('barbers/<str:pk>/edit/', admin_views.admin_barber_edit, name='admin_barber_edit'),
    path('barbers/<str:pk>/delete/', admin_views.admin_barber_delete, name='admin_barber_delete'),
    path('testimonials/', admin_views.admin_testimonials, name='admin_testimonials'),
    path('testimonials/<str:pk>/approve/', admin_views.approve_testimonial, name='approve_testimonial'),
    path('analytics/', admin_views.admin_analytics, name='admin_analytics'),
    path('availability/', admin_views.admin_availability, name='admin_availability'),
    path('availability/data/', get_available_slots, name='admin_availability_data'),
    path('haircut-styles/', admin_views.admin_haircut_styles, name='admin_haircut_styles'),
    path('haircut-styles/add/', admin_views.admin_haircut_style_add, name='admin_haircut_style_add'),
    path('haircut-styles/<str:pk>/edit/', admin_views.admin_haircut_style_edit, name='admin_haircut_style_edit'),
    path('haircut-styles/<str:pk>/delete/', admin_views.admin_haircut_style_delete, name='admin_haircut_style_delete'),
    path('services/', admin_views.admin_services, name='admin_services'),
    path('services/add/', admin_views.admin_service_add, name='admin_service_add'),
    path('services/<str:pk>/edit/', admin_views.admin_service_edit, name='admin_service_edit'),
    path('services/<str:pk>/delete/', admin_views.admin_service_delete, name='admin_service_delete'),
    path('about/', admin_views.admin_about_edit, name='admin_about_edit'),
    path('services-page/', admin_views.admin_services_page_edit, name='admin_services_page_edit'),
]
