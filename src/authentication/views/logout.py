from django.shortcuts import render
from django.http import HttpRequest, HttpResponseBadRequest
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


@login_required
def logout_view(request: HttpRequest):
    if request.POST:
        logout(request)
        return render(request, 'authentication/logout.html')

    return HttpResponseBadRequest()
