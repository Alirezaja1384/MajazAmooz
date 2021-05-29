from django.urls import path

from user.views import (
    home_view, TutorialListView,
    TutorialDetailView, TutorialCreateView,
    TutorialUpdateView, TutorialDeleteView
)


app_name = 'user'

urlpatterns = [
    path('', home_view, name='home'),

    path('tutorials/', TutorialListView.as_view(
        extra_context={'title': 'مدیریت آموزش ها'}), name='tutorials'),

    path('tutorials/create', TutorialCreateView.as_view(
        extra_context={'title': 'افزودن آموزش'}), name='tutorial_create'),

    path('tutorials/edit/<int:pk>', TutorialUpdateView.as_view(
        extra_context={'title': 'ویرایش آموزش'}), name='tutorial_update'),

    path('tutorials/delete/<int:pk>', TutorialDeleteView.as_view(
        extra_context={'title': 'حذف آموزش'}), name='tutorial_delete'),

    path('tutorials/details/<int:pk>', TutorialDetailView.as_view(
        extra_context={'title': 'اطلاعات آموزش'}), name='tutorial_details'),
]
