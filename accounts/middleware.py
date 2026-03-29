from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.signed_cookies import SessionStore


class MongoAuthMiddleware:
    """
    Lightweight auth middleware for MongoDB/MongoEngine setup.
    Attaches request.user from the session
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, 'user'):
            request.user = self._get_user(request)
        response = self.get_response(request)
        return response

    def _get_user(self, request):
        from django.contrib.auth import get_user
        try:
            return get_user(request)
        except Exception:
            return AnonymousUser()