# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User, Group
from django.urls import reverse

# from apps.analyst.models import AlarmType


class Menu(models.Model):
    # itemid = models.IntegerField()
    parentid = models.IntegerField()
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    itemorder = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField()
    is_seen = models.BooleanField()
    has_item = models.BooleanField()
    icon = models.CharField(max_length=50, null=True)
    alarmtype_ids = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ["id"],
        constraints = [
            models.UniqueConstraint(fields=['address'], name='menu_address_unique'),
            # models.UniqueConstraint(fields=['userid'], name='umenu_user_unique')
        ]


# class MenuAlarmType(models.Model):
#     menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
#     alarmtype = models.ForeignKey(AlarmType, on_delete=models.CASCADE)


# class UserMenu(models.Model):
#     userid = models.IntegerField()
#     groupid = models.IntegerField()
#     usermenu = models.CharField(max_length=250, default='')
#
#     class Meta:
#         constraints = [
#             # models.UniqueConstraint(fields=['groupid'], name='umenu_group_unique'),
#             # models.UniqueConstraint(fields=['userid'], name='umenu_user_unique')
#         ]


class Company(models.Model):
    name = models.CharField(max_length=200)
    linkedinname = models.CharField(max_length=200)
    shodanname = models.CharField(max_length=200)
    licensetype = models.CharField(max_length=50)
    licensestartdate = models.DateField()
    licenseenddate = models.DateField()
    country = models.CharField(max_length=100)
    activityarea = models.CharField(max_length=100)
    securitygrade = models.CharField(max_length=100)
    companysize = models.CharField(max_length=100)
    logo = models.ImageField(blank=True, null=True)
    email = models.CharField(max_length=100)
    username = models.CharField(max_length=50, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    apikey = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='company_name_unique'),
            # models.UniqueConstraint(fields=['apikey'], name='company_apikey_unique')
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('home:company_create')
        # return "/post/{}".format(self.id)

    def get_file_path(self):
        return self.logo


class Country(models.Model):
    sname = models.CharField(max_length=5)
    name = models.CharField(max_length=150)
