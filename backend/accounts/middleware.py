from django.contrib.sessions.models import Session
from django.utils.deprecation import MiddlewareMixin


class SingleSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            current_session_key = request.session.session_key

            user_profile = request.user.userprofile

            if user_profile.session_key and user_profile.session_key != current_session_key:
                Session.objects.filter(session_key=user_profile.session_key).delete()

            user_profile.session_key = current_session_key
            user_profile.save()