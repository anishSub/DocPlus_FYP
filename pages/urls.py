from django.contrib import admin
from django.urls import path
from .views import HomeView, AboutUsView, ContactUsView, ProfileView, ProfileEditView


urlpatterns = [
    # path('', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('about-us/', AboutUsView.as_view(), name='about_us'),
    path('contact-us/', ContactUsView.as_view(), name='contact_us'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
]
