from django.urls import path, re_path

from apps import home
from apps.analyst import views

urlpatterns = [
    # The home page
    path('', home.views.index, name='home'),
    path('alarmtypes/', views.alarmtypes, name='alarmtypes'),
    path('get_alarm_type/', views.get_alarm_type, name='get_alarm_type'),
    # path('companies/create', views.company_create, name='company_create'),
    path('alarmtypes/update/<int:id>/', views.alarmtype_update, name='alarmtype_update'),
    path('alarmtypes/delete/', views.alarmtype_delete, name='alarmtype_delete'),
    path('contenttypes/', views.content_type_create, name='content_type_create'),
    path('get_contents/', views.get_contents, name='get_contents'),
    path('alarms/', views.alarms, name='alarms'),
    path('get_alarm/', views.get_alarm, name='get_alarm'),
    path('alarms/delete/', views.alarm_delete, name='alarm_delete'),
]
