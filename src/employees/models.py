from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.core.exceptions import PermissionDenied
from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.utils.itercompat import is_iterable
from django.utils.translation import gettext_lazy as _

from employees.validators import UsernameValidator


class Position(models.Model):
    name = models.CharField('Наименование', max_length=64)
    role = models.ForeignKey(Group,
                             on_delete=models.SET_NULL,
                             null=True,
                             verbose_name='Роль',
                             related_name='positions'
                             )

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.name


def _user_get_permissions(user, obj, from_name):
    permissions = set()
    name = "get_%s_permissions" % from_name
    for backend in auth.get_backends():
        if hasattr(backend, name):
            permissions.update(getattr(backend, name)(user, obj))
    return permissions


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, "has_perm"):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, "has_module_perms"):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                return True
        except PermissionDenied:
            return False
    return False


class PermissionsMixin(models.Model):
    is_superuser = models.BooleanField(
        _('Статус суперпользователя'),
        default=False,
        help_text=_(
            'Определяет, является ли данный пользователь суперпользователем.'
        )
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("Права пользователя"),
        blank=True,
        related_name="user_set",
        related_query_name="user",
    )

    class Meta:
        abstract = True

    def get_user_permissions(self, obj=None):
        return _user_get_permissions(self, obj, "user")

    def get_group_permissions(self, obj=None):
        return _user_get_permissions(self, obj, "group")

    def get_all_permissions(self, obj=None):
        return _user_get_permissions(self, obj, "all")

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_superuser:
            return True

        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        if not is_iterable(perm_list) or isinstance(perm_list, str):
            raise ValueError("perm_list must be an iterable of permissions.")
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)


class EmployeeManager(BaseUserManager):
    def create_user(self, username: str, password: str, FIO: str, salary: int,
                    phone_number: str, address: str, **extra_fields):
        if not username:
            raise ValueError(_('Имя пользователя должно быть установлено'))

        if not password:
            raise ValueError(_('Пароль должен быть установлен'))

        user = self.model(username=username,
                          password=password,
                          FIO=FIO,
                          salary=salary,
                          phone_number=phone_number,
                          address=address,
                          **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username: str, password: str, FIO: str, salary: int,
                         phone_number: str, address: str, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, FIO, salary, phone_number, address, **extra_fields)

    # Имя пользователя нечувствительно к регистру
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD.casefold(): username.casefold()})


class Employee(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('Имя пользователя'),
        max_length=16,
        unique=True,
        error_messages={
            'unique': _('Пользователь с таким именем уже зарегистрирован')
        },
        validators=[MinLengthValidator(3), UsernameValidator()],
    )
    password = models.CharField(_('Пароль'), max_length=128)
    FIO = models.CharField('ФИО', max_length=100)
    position = models.ForeignKey(Position,
                                 on_delete=models.PROTECT,
                                 related_name='employees',
                                 verbose_name='Должность',
                                 null=True
                                 )
    salary = models.PositiveIntegerField('Зарплата')
    address = models.CharField('Адрес', max_length=64)
    phone_number = models.CharField('Номер телефона', max_length=10)
    is_staff = models.BooleanField(
        _('Статус персонала'),
        default=False,
        help_text=_(
            'Определяет, является ли данный пользователь членом персонала'
        )
    )
    is_active = models.BooleanField(_('Активный пользователь'), default=True)
    registered = models.DateTimeField(_('Дата регистрации'), auto_now_add=True)
    last_login = models.DateTimeField(_('Последний вход'), blank=True, null=True)

    objects = EmployeeManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['FIO', 'salary', 'address', 'phone_number']

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.FIO


class Salary(models.Model):
    year = models.PositiveIntegerField('Год')
    month = models.PositiveIntegerField('Месяц')
    employee = models.ForeignKey(Employee,
                                 on_delete=models.PROTECT,
                                 related_name='salaries',
                                 verbose_name='Сотрудник')
    procurements = models.PositiveIntegerField('Количество закупок')
    productions = models.PositiveIntegerField('Количество производств')
    sales = models.PositiveIntegerField('Количество продаж')
    common = models.PositiveIntegerField('Общее количество участий')
    bonus = models.FloatField('Бонус')
    general = models.PositiveIntegerField('К выдаче')
    is_issued = models.BooleanField('Выдано', default=False)

    class Meta:
        verbose_name = 'Зарплата'
        unique_together = ('year', 'month', 'employee')

    def __str__(self):
        return f'{self.year} {self.month} {self.employee} {self.general} {self.is_issued}'
