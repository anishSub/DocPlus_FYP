"""
URL configuration for myproject project.

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
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('', include('pages.urls')),
    path('find_doctor/', include('find_doctor.urls')),
    path('find_hospital/', include('find_hospital.urls')),
    path('appointments/', include('appointments.urls')),
    path('doctorAdmin/', include('doctorAdmin.urls')),
    path('superAdmin/', include('superAdmin.urls')),
    path('accounts/', include('allauth.urls')),
]

# This allows you to view uploaded files while developing
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
