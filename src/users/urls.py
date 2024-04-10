from django.contrib.auth.views import LogoutView
from django.urls import path

from users.views import UserLoginView, UserRegisterView

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page='main:index'), name='logout'),
]
