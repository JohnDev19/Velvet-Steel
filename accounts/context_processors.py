from .models import UserProfile


def user_profile(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects(user_id=request.user.pk).first()
        except Exception:
            profile = None
        return {'user_profile': profile}
    return {'user_profile': None}
