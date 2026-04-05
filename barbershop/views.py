from django.shortcuts import render
from reservations.models import Barber, HaircutStyle, Service, Testimonial, GalleryImage
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


def _site_info():
    from reservations.models import SiteSettings
    try:
        s = SiteSettings.get()
        return {
            'shop_name':    s.shop_name,
            'shop_phone':   s.footer_phone,
            'shop_address': s.footer_address,
            'shop_email':   s.footer_email,
        }
    except Exception:
        return {
            'shop_name':    'Velvet Steel Barbershop',
            'shop_phone':   '',
            'shop_address': '',
            'shop_email':   '',
        }


def home(request):
    from reservations.models import HomePage
    home_page = HomePage.objects().first()
    barbers  = Barber.objects(is_active=True)
    services = Service.objects(is_active=True).order_by('category', 'price')
    testimonials = list(Testimonial.objects(is_approved=True).order_by('-created_at')[:9])
    photos = _testimonial_photos(testimonials)
    for t in testimonials:
        t.cust_photo = photos.get(t.customer_username, '')
    gallery_images = list(GalleryImage.objects().order_by('-is_featured', '-created_at')[:8])
    context = {
        'barbers':        barbers,
        'services':       services,
        'testimonials':   testimonials,
        'home_page':      home_page,
        'gallery_images': gallery_images,
        'gallery_ready':  len(gallery_images) >= 8,
        **_site_info(),
    }
    return render(request, 'home/index.html', context)


def about(request):
    from reservations.models import AboutPage
    barbers = Barber.objects(is_active=True)
    about   = AboutPage.objects().first()
    context = {
        'barbers': barbers,
        'about':   about,
        **_site_info(),
    }
    return render(request, 'about/index.html', context)

def privacy_policy(request):
    from reservations.models import PrivacyPage
    page = PrivacyPage.get()
    return render(request, 'home/privacy.html', {'page': page})


def terms_of_service(request):
    from reservations.models import TermsPage
    page = TermsPage.get()
    return render(request, 'home/terms.html', {'page': page})


def services(request):
    from reservations.models import ServicesPage
    svc_page = ServicesPage.objects().first()
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
        'svc_page':           svc_page,
        **_site_info(),
    }
    return render(request, 'home/services.html', context)
