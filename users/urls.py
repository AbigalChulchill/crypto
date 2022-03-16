from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('registeration/', views.registeration, name="Registeration"),
    path('login/', auth_views.LoginView.as_view(template_name="pages/users/login.html"), name="Login"),
    path('logout/', auth_views.LogoutView.as_view(template_name="pages/users/logout.html"), name="Logout"),
]