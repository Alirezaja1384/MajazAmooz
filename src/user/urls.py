from django.urls import path

from user.views import (
    home_view, TutorialListView,
    TutorialDetailView
)


app_name = 'user'

urlpatterns = [
    path('', home_view, name='home'),
    path('tutorials/', TutorialListView.as_view(
        extra_context={'title': 'مدیریت آموزش ها'}), name='tutorials'),
    path('tutorials/details/<int:pk>', TutorialDetailView.as_view(
        extra_context={'title': 'اطلاعات آموزش'}),name='tutorial_details'),
]
