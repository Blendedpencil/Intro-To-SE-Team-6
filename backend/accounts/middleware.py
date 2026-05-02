from django.contrib.sessions.models import Session
from django.utils.deprecation import MiddlewareMixin


class SingleSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'userprofile', None)

            if profile and profile.session_key:
                if profile.session_key != request.session.session_key:
                    from django.contrib.auth import logout
                    logout(request)

            if profile:
                profile.session_key = request.session.session_key
                profile.save()

        response = self.get_response(request)
        return response