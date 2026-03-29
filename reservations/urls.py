from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_reservation, name='book_reservation'),
    path('my/', views.my_reservations, name='my_reservations'),
    path('<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('api/slots/', views.get_available_slots, name='get_available_slots'),
    path('testimonial/', views.submit_testimonial, name='submit_testimonial'),
]
