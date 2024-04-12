from django.template import Library

from employees.models import Employee as User

register = Library()


@register.filter
def has_permission(user: User, permission):
    return user.has_perm(permission)
