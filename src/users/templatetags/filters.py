from django.contrib.auth.models import User
from django.template import Library

register = Library()


@register.filter
def has_permission(user: User, permission):
    return user.has_perm(permission)
