from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, Group
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.db import models

from users.validators import UsernameValidator


class UserManager(BaseUserManager):
    def create_user(self, username: str, email: str, password: str, **extra_fields) -> 'User':
        if not username:
            raise ValueError(_('Имя пользователя должно быть установлено'))

        if not email:
            raise ValueError(_('Email-адрес должен быть установлен'))

        if not password:
            raise ValueError(_('Пароль должен быть установлен'))

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, password=password, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username: str, email: str, password: str, **extra_fields) -> 'User':
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

    # Имя пользователя нечувствительно к регистру
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD.casefold(): username.casefold()})


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('Имя пользователя'),
        max_length=16,
        unique=True,
        error_messages={
            'unique': _('Пользователь с таким именем уже зарегистрирован')
        },
        validators=[MinLengthValidator(4), UsernameValidator()],
    )
    email = models.EmailField(
        _('Электронная почта'),
        unique=True,
        error_messages={
            'unique': _('Пользователь с такой почтой уже зарегистрирован')
        }
    )
    password = models.CharField(_('Пароль'), max_length=128)
    is_staff = models.BooleanField(
        _('Статус персонала'),
        default=False,
        help_text=_(
            'Определяет, является ли данный пользователь членом персонала'
        )
    )
    is_active = models.BooleanField(_('Активный пользователь'), default=True)
    is_superuser = models.BooleanField(
        _('Статус суперпользователя'),
        default=False,
        help_text=_(
            'Определяет, является ли данный пользователь суперпользователем.'
        )
    )
    registered = models.DateTimeField(_('Дата регистрации'), auto_now_add=True)
    last_login = models.DateTimeField(_('Последний вход'), blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.username
