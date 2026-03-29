from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

admin_urls = admin.site.urls
urlpatterns = [
    path('django-admin/', include((admin_urls[0], 'django-admin'), namespace='django-admin')),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('reservations/', include('reservations.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin-panel/', include('reservations.admin_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)