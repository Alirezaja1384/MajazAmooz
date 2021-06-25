from .base import DEBUG

if DEBUG:
    from .development import *
else:
    from .production import *
