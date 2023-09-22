# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.contrib.auth.models import Group, User
from django.db import models

from apps.home.models import Menu, Company


class MyGroup(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    menus = models.ManyToManyField(Menu, through='GroupMenu')


class GroupMenu(models.Model):
    group = models.ForeignKey(MyGroup, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)


class MyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    companies = models.ManyToManyField(Company, through='UserCompany')


class UserCompany(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
