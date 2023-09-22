# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path

from core import settings
from .views import login_view, register_user, forgot_pass
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path('forgot/', forgot_pass, name="forgot"),
    # path("logout/", LogoutView.as_view(), name="logout")
    path('logout/', auth_views.logout_then_login, name='logout'),
]
