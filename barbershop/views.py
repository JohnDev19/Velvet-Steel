from django.shortcuts import render
from django.conf import settings
from reservations.models import Service, Barber, HaircutStyle
from collections import defaultdict


def home(request):
    services = Service.objects.filter(is_active=True)[:6]
    barbers = Barber.objects.filter(is_active=True)[:3]
    context = {
        'services': services,
        'barbers': barbers,
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
    all_services = Service.objects.filter(is_active=True)
    all_styles = HaircutStyle.objects.filter(is_active=True)

    styles_by_category = defaultdict(list)
    for style in all_styles:
        styles_by_category[style.get_category_display()].append(style)
    styles_by_category = dict(styles_by_category)

    context = {
        'services': all_services,
        'styles_by_category': styles_by_category,
        'has_styles': all_styles.exists(),
        'shop_name': settings.BARBERSHOP_NAME,
    }
    return render(request, 'home/services.html', context)
