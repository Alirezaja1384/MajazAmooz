""" Learn home view """
from django.http import HttpRequest
from django.shortcuts import render

def home_view(request: HttpRequest):
    """ Home view """
    return render(request, 'learning/home.html')
