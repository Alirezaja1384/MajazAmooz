from .base import *  # noqa
from .base import BASE_DIR


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
# Note: You can change STATIC_URL and MEDIA_URL in base.py

# Media files
MEDIA_ROOT = BASE_DIR / "media/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
