from django.contrib import admin

# Register your models here.
from apps.analyst.models import Alarm

admin.site.register(Alarm)
