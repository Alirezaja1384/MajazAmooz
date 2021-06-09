from django.urls import path

from user import views


app_name = 'user'

urlpatterns = [
    path('', views.home_view, name='home'),

    path('tutorials/', views.TutorialListView.as_view(
        extra_context={'title': 'مدیریت آموزش ها'}), name='tutorials'),

    path('tutorials/create', views.TutorialCreateView.as_view(
        extra_context={'title': 'افزودن آموزش'}), name='tutorial_create'),

    path('tutorials/edit/<int:pk>', views.TutorialUpdateView.as_view(
        extra_context={'title': 'ویرایش آموزش'}), name='tutorial_update'),

    path('tutorials/details/<int:pk>', views.TutorialDetailView.as_view(
        extra_context={'title': 'اطلاعات آموزش'}), name='tutorial_details'),

    path('tutorials/delete/<int:pk>', views.TutorialDeleteDeactivateView.as_view(
        extra_context={'title': 'حذف آموزش'}), name='tutorial_delete'),

    path('tutorials/tutorials_viewed_by_others', views.TutorialsViewedByOthersListView.as_view(
        extra_context={'title': 'بازدید های دیگران از آموزش های شما'}),
        name='tutorials_viewed_by_others'),

    path('tutorials/tutorials_liked_by_others', views.TutorialsLikedByOthersListView.as_view(
        extra_context={'title': 'لایک های دیگران برای آموزش های شما'}),
        name='tutorials_liked_by_others'),

    path('tutorials/tutorials_liked_by_me', views.TutorialsLikedByMeListView.as_view(
        extra_context={'title': 'آموزش های لایک شده توسط شما'}),
        name='tutorials_liked_by_me'),

    path('tutorial_comments/', views.TutorialCommentListView.as_view(
        extra_context={'title': 'مدیریت دیدگاه آموزش ها'}), name='tutorial_comments'),

    path('tutorial_comments/detail/<int:pk>', views.TutorialCommentDetailsView.as_view(
        extra_context={'title': 'اطلاعات دیدگاه آموزش'}), name='tutorial_comment_details'),

    path('tutorial_comments/edit/<int:pk>', views.TutorialCommentUpdateView.as_view(
        extra_context={'title': 'ویرایش دیدگاه آموزش'}), name='tutorial_comment_update'),

]
