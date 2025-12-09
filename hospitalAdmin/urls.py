from django.urls import path
from .views import HospitalAdminOverview

urlpatterns = [
    path( 'Hospital-Admin/',HospitalAdminOverview.overview, name='hospital_admin_overview')
]
