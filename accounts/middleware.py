from django.contrib.auth.models import AnonymousUser

class MongoAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, 'user'):
            request.user = AnonymousUser()
        return self.get_response(request)