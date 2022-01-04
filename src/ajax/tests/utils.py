from typing import Optional, Dict
from django.http import HttpRequest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from authentication.models import User


DEFAULT_USER = AnonymousUser()


def ajax_request(
    data: Optional[Dict] = None, user: Optional[User] = DEFAULT_USER
) -> HttpRequest:
    factory = RequestFactory()
    request = factory.post(
        "/",
        data=data or dict(),
        content_type="application/json",
        # This request will be detected as ajax request
        # because of its Accept header.
        **{"HTTP_ACCEPT": "application/json"}
    )
    request.user = user

    return request
