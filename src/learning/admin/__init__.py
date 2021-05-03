from django.conf import settings
from .actions import (
    confirm_action,
    disprove_action
)

if settings.DEBUG:
    from .development import *
else:
    from .production import *
