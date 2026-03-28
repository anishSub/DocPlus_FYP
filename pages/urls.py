from django.contrib import admin
from django.urls import path
from .views import HomeView, AboutUsView, ContactUsView, ProfileView, ProfileEditView, GlobalSearchView, ToggleFavoriteDoctorView, ToggleFavoriteHospitalView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about-us/', AboutUsView.as_view(), name='about_us'),
    path('contact-us/', ContactUsView.as_view(), name='contact_us'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('api/global-search/', GlobalSearchView.as_view(), name='global_search'),
    path('api/toggle-favorite-doctor/<int:doctor_id>/', ToggleFavoriteDoctorView.as_view(), name='toggle_favorite_doctor'),
    path('api/toggle-favorite-hospital/<int:hospital_id>/', ToggleFavoriteHospitalView.as_view(), name='toggle_favorite_hospital'),
]
