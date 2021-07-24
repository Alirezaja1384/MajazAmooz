"""
    Learning urls
"""
from django.urls import path, re_path
from .views import HomeView, TutorialDetailsView, TutorialListView


app_name = "learning"
UNICODE_SLUG_REGEX = r"\w-"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    re_path(
        f"^tutorial/(?P<slug>[{UNICODE_SLUG_REGEX}]+)$",
        TutorialDetailsView.as_view(),
        name="tutorial",
    ),
    path(
        "tutorials_archive",
        TutorialListView.as_view(),
        name="tutorials_archive",
    ),
]
