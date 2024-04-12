import re

from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class UsernameValidator(RegexValidator):
    regex = r'^[a-zA-Z][a-zA-Z0-9_]*$'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and _ characters. It must start with a letter.'
    )
    flags = re.ASCII
