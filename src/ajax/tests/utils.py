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
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    request.user = user

    return request
