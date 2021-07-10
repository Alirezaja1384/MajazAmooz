from .base import DEBUG

if DEBUG:
    from .development import *  # noqa
else:
    from .production import *  # noqa
