""" Learn home view """
from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.cache import cache_page


@cache_page(60 * 5)
def home_view(request: HttpRequest):
    """ Home view """
    return render(request, 'learning/home.html')
