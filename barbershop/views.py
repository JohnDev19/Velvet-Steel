from django.shortcuts import render
from django.conf import settings
from reservations.models import Barber, HaircutStyle, Service, Testimonial
from accounts.models import UserProfile
from django.contrib.auth.models import User
from collections import defaultdict


def _testimonial_photos(testimonials):
    photos = {}
    for t in testimonials:
        if t.customer_username:
            try:
                dj = User.objects.filter(username=t.customer_username).first()
                if dj:
                    prof = UserProfile.objects(user_id=dj.pk).first()
                    if prof and prof.photo:
                        photos[t.customer_username] = prof.photo
            except Exception:
                pass
    return photos


def home(request):
    barbers  = Barber.objects(is_active=True)
    services = Service.objects(is_active=True).order_by('category', 'price')
    testimonials = list(Testimonial.objects(is_approved=True).order_by('-created_at')[:9])
    photos = _testimonial_photos(testimonials)
    for t in testimonials:
        t.cust_photo = photos.get(t.customer_username, '')
    context = {
        'barbers':      barbers,
        'services':     services,
        'testimonials': testimonials,
        'shop_name':    settings.BARBERSHOP_NAME,
        'shop_phone':   settings.BARBERSHOP_PHONE,
        'shop_address': settings.BARBERSHOP_ADDRESS,
    }
    return render(request, 'home/index.html', context)


def about(request):
    barbers = Barber.objects(is_active=True)
    context = {
        'barbers':      barbers,
        'shop_name':    settings.BARBERSHOP_NAME,
        'shop_phone':   settings.BARBERSHOP_PHONE,
        'shop_address': settings.BARBERSHOP_ADDRESS,
        'shop_email':   settings.BARBERSHOP_EMAIL,
    }
    return render(request, 'about/index.html', context)


def services(request):
    all_styles = HaircutStyle.objects(is_active=True)

    styles_by_category = defaultdict(list)
    for style in all_styles:
        styles_by_category[style.get_category_display()].append(style)
    styles_by_category = dict(styles_by_category)

    all_services = Service.objects(is_active=True).order_by('category', 'price')

    context = {
        'styles_by_category': styles_by_category,
        'has_styles':         all_styles.count() > 0,
        'all_services':       all_services,
        'has_services':       all_services.count() > 0,
        'shop_name':          settings.BARBERSHOP_NAME,
    }
    return render(request, 'home/services.html', context)