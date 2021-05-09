from django.shortcuts import render
from django.http import HttpRequest, HttpResponseBadRequest
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


@login_required
def logout_view(request: HttpRequest):
    if request.POST:
        logout(request)

        # If next parameter sent and
        # it was local redirect user
        next_url = request.POST.get('next', '')

        return render(request, 'authentication/logout.html',{
            'next': next_url if next_url.startswith('/') else ''
        })

    return HttpResponseBadRequest()
