# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include, re_path  # add this
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets


# Serializers define the API representation.
from apps.home import views
from django.conf import settings
from django.conf.urls.static import static


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path("", views.index, name="home"),
    path("admin/", admin.site.urls),          # Django admin route
    path("auth/", include("apps.authentication.urls")),  # Auth routes - login / register
    path("home/", include(("apps.home.urls", "apps.home"), namespace="home")),       # UI Kits Html files
    path("iocs/", include(("apps.iocs.urls", "apps.iocs"), namespace="iocs")),
    path("analyst/", include(("apps.analyst.urls", "apps.analyst"), namespace="analyst")),
    path("rest/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
