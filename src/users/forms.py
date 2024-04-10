from django import forms

from users.models import User


class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
