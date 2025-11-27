from django.contrib import admin
from django.urls import path
from .views import HomeView, AboutUsView, ContactUsView, FindDoctorView, FindHospitalView


urlpatterns = [
    # path('', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    # path('', ExampleView.as_view(), name='example'),
    path('about-us/', AboutUsView.as_view(), name='about_us'),
    path('contact-us/', ContactUsView.as_view(), name='contact_us'),
    path('find-doctor/', FindDoctorView.as_view(), name='find_doctor'),
    path('find-hospital/', FindHospitalView.as_view(), name='find_hospital'),
]
