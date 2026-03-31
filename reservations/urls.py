from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_reservation, name='book_reservation'),
    path('my/', views.my_reservations, name='my_reservations'),
    path('review/', views.review_page, name='review_page'),
    path('api/slots/', views.get_available_slots, name='get_available_slots'),
    path('testimonial/', views.submit_testimonial, name='submit_testimonial'),
    path('<str:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('<str:pk>/', views.reservation_detail, name='reservation_detail'),
]