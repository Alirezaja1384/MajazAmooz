from django.conf import settings

if settings.DEBUG:
    from .development import *  # noqa
else:
    from .production import *  # noqa
