from django.contrib import admin
from django.urls import path
from .views import HomeView, AboutUsView, ContactUsView, ProfileView, ProfileEditView, GlobalSearchView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about-us/', AboutUsView.as_view(), name='about_us'),
    path('contact-us/', ContactUsView.as_view(), name='contact_us'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('api/global-search/', GlobalSearchView.as_view(), name='global_search'),
]
