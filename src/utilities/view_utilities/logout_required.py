from django.shortcuts import redirect
from django.http import HttpRequest
from django.conf import settings


class LogoutRequiredMixin():
    """
        Redirects user to LOGOUT_REQUIRED_URL
        set in settings if was authenticated
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs):

        # If user was authenticated redirect
        # to logout required url
        if request.user.is_authenticated:
            next_url = request.GET.get('next') or request.path
            return redirect(settings.LOGOUT_REQUIRED_URL + "?next=" + next_url)

        return super().dispatch(request, *args, **kwargs)
