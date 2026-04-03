from .models import UserProfile


def user_profile(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects(user_id=request.user.pk).first()
        except Exception:
            profile = None
        return {'user_profile': profile}
    return {'user_profile': None}


def site_settings(request):
    try:
        from reservations.models import SiteSettings
        settings = SiteSettings.get()
    except Exception:
        settings = None

    site_logo = None
    try:
        from django.contrib.auth.models import User
        staff_user = User.objects.filter(is_staff=True).order_by('pk').first()
        if staff_user:
            admin_profile = UserProfile.objects(user_id=staff_user.pk).first()
            if admin_profile and admin_profile.photo:
                site_logo = admin_profile.photo
    except Exception:
        pass

    return {'site_settings': settings, 'site_logo': site_logo}