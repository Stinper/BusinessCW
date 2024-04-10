from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView

from users.forms import UserRegisterForm
from users.models import User


class UserLoginView(LoginView):
    template_name = 'users/user-login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('main:index')


class UserRegisterView(FormView):
    template_name = 'users/user-register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('main:index')

    def form_valid(self, form):
        user = User.objects.create_user(username=form.cleaned_data['username'],
                                        email=form.cleaned_data['email'],
                                        password=form.cleaned_data['password']
                                        )
        login(self.request, user)
        return super(UserRegisterView, self).form_valid(form)
