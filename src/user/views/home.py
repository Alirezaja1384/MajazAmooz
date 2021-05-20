from django.shortcuts import render
from django.http import HttpRequest


def home_view(request:HttpRequest):
    return render(request, 'user/home.html')
