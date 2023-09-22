# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.urls import path, re_path
from apps.home import views

urlpatterns = [
    # The home page
    path('', views.index, name='home'),
    path('companies/', views.companies, name='companies'),
    # path('companies/create', views.company_create, name='company_create'),
    # path('companies/update/<int:id>/', views.company_update, name='company_update'),
    # path('getcompany/<int:id>/', views.getcompany, name='getcompany'),
    path('companies/delete/<int:id>/', views.company_delete, name='company_delete'),
    path('companies/users/<int:id>/', views.company_users, name='company_users'),
    path('users/', views.users, name='users'),
    # path('users/create', views.user_create, name='user_create'),
    # path('users/update/<int:id>/', views.user_update, name='user_update'),
    # path('users/delete/<int:id>/', views.user_delete, name='user_delete'),
    path('users/delete/', views.user_delete, name='user_delete'),
    path('users/companies/<int:id>/', views.user_companies, name='user_companies'),
    path('menus/', views.menus, name='menus'),
    # path('users/create', views.user_create, name='user_create'),
    path('menus/update/<int:id>/', views.menu_update, name='menu_update'),
    path('menus/delete/<int:id>/', views.menu_delete, name='menu_delete'),
    path('rolemenu/', views.role_menu, name='role_menu'),

    # path('friends/', views.indexView),
    # path('post/ajax/friend', views.post_friend, name="post_friend"),
    # path('get/ajax/validate/nickname', views.checknickname, name="checknickname"),
    path('get/ajax/menu', views.get_user_menu, name="get_user_menu"),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
]
