import re
from django.conf import settings
from django.http import HttpResponseRedirect


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.urls = [
            re.compile(url)
            for url in getattr(settings, "LOGIN_REQUIRED_URLS", [])
        ]

        self.login_url = getattr(settings, "LOGIN_URL", "/auth/login/")

    def __call__(self, request):

        for url in self.urls:
            if url.match(request.path) and request.user.is_anonymous:
                return HttpResponseRedirect(
                    "{}?next={}".format(self.login_url, request.path)
                )

        return self.get_response(request)
