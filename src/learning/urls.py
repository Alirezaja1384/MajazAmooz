"""
    Learning urls
"""
from django.urls import path, re_path

from .views import (
    home_view, tutorial_details_view,
    TutorialListView
)

app_name = 'learning'

UNICODE_SLUG_REGEX = r"\w-"

urlpatterns = [
    path('', home_view, name='home'),
    re_path(f"^tutorial/(?P<slug>[{UNICODE_SLUG_REGEX}]+)$",
            tutorial_details_view, name='tutorial'),
    path('tutorials_archive', TutorialListView.as_view(),
         name='tutorials_archive')
]
