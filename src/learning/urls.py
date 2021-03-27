"""
    Learning urls
"""

from django.contrib import admin
from django.urls import path

from .views import home_view

app_name = 'learning'

urlpatterns = [
    path('', home_view, name='home')
]
