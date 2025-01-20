"""
URL configuration for fetest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView
from rest_framework import routers
from django.urls import include
import profiles.views as profile_views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', profile_views.EmployeeView.as_view(), name='home'),
    path('employees/', profile_views.EmployeeView.as_view(), name='employees'),
    path('random/', profile_views.random_view),
]

urlpatterns += [
    path('accounts/', include('accounts.urls')),
]

router = routers.DefaultRouter()
router.register('api/employees', profile_views.EmployeeViewSet)
employee_list_url = path('api/employees/', profile_views.EmployeeViewSet.as_view({'get': 'list'}), name='employee-list')
urlpatterns += [employee_list_url]
urlpatterns += router.urls

api_docs = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/documentation/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
urlpatterns += api_docs