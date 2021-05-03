from django.conf import settings

if settings.DEBUG:
    from .development import *
else:
    from .production import *
