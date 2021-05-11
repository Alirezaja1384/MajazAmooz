from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required


@login_required
def logout_required_view(request: HttpRequest):
    return render(request, 'authentication/logout_required.html', {
        'next': request.GET.get('next', '')
    })
