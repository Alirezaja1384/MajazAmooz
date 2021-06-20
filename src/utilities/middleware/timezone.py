import pytz

from django.utils import timezone
from django.conf import settings


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # get default user timezone from settins. defaults to settings TIME_ZONE
        default_timezone = getattr(settings, 'DEFAULT_USER_TZ', settings.TIME_ZONE)
        # Try to get timezone from user's session
        tz_name = request.session.get('timezone', default_timezone)
        # Activate timezone
        timezone.activate(pytz.timezone(tz_name))

        return self.get_response(request)
