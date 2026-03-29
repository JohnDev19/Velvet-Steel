from django.shortcuts import render
from django.conf import settings
from reservations.models import Service, Barber, Testimonial


def home(request):
    services = Service.objects.filter(is_active=True)[:6]
    barbers = Barber.objects.filter(is_active=True)[:3]
    testimonials = Testimonial.objects.filter(is_approved=True)[:4]
    context = {
        'services': services,
        'barbers': barbers,
        'testimonials': testimonials,
        'shop_name': settings.BARBERSHOP_NAME,
        'shop_phone': settings.BARBERSHOP_PHONE,
        'shop_address': settings.BARBERSHOP_ADDRESS,
    }
    return render(request, 'home/index.html', context)


def about(request):
    barbers = Barber.objects.filter(is_active=True)
    context = {
        'barbers': barbers,
        'shop_name': settings.BARBERSHOP_NAME,
        'shop_phone': settings.BARBERSHOP_PHONE,
        'shop_address': settings.BARBERSHOP_ADDRESS,
        'shop_email': settings.BARBERSHOP_EMAIL,
    }
    return render(request, 'about/index.html', context)


def services(request):
    services = Service.objects.filter(is_active=True)
    context = {
        'services': services,
        'shop_name': settings.BARBERSHOP_NAME,
    }
    return render(request, 'home/services.html', context)
