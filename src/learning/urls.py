"""
    Learning urls
"""
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    home_view, TutorialDetailView
)

app_name = 'learning'

UNICODE_SLUG_REGEX = r"\w-"

urlpatterns = [
    path('', home_view, name='home'),
    re_path(f"^tutorial/(?P<slug>[{UNICODE_SLUG_REGEX}]+)$",
            TutorialDetailView.as_view(), name='tutorial'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
