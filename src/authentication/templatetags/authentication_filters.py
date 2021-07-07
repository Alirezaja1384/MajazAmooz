""" Authentication template filters """
from django import template

from authentication.models import User

register = template.Library()


@register.filter
def full_name(user: User):
    """
    @param user: User instance
    @return: user's full name
    """
    return f"{user.first_name} {user.last_name}" if user else "ناشناس"
