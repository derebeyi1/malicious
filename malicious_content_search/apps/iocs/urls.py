from django.urls import path, re_path, include

from apps import home
from apps.iocs import views

app_name = 'apps.iocs'

urlpatterns = [
    # path('', views.index, name='home'),
    path('', views.iocs_index, name='index'),
    path("auth/", include("apps.authentication.urls")),  # Auth routes - login / register
    # path(r'starter/', views.iocs_starter, name='starter'),
    path(r'search/', views.iocs_search, name='search'),
    # path(r'index1/', views.iocs_index1, name='index1'),
    path(r'index/', views.iocs_index, name='index'),
    # path("home/", include(("apps.home.urls", "apps.home"), namespace='home')),
    # re_path(r'^.*\.*', home.views.pages, name='pages'),
    # path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('dist/img/favicon.ico')))
    # # path(r'index2/', views.index2, name='index2'),
    # # path('', views.index, name='index'),
    # # path('home/', views.index, name='home'),
]