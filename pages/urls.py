from django.contrib import admin
from django.urls import path
from .views import HomeView, AboutUsView, ContactUsView


urlpatterns = [
    # path('', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('about-us/', AboutUsView.as_view(), name='about_us'),
    path('contact-us/', ContactUsView.as_view(), name='contact_us'),
]
