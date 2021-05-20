from django.urls import path

from user.views import home_view


app_name = 'user'

urlpatterns = [
    path('', home_view, name='home'),
]
