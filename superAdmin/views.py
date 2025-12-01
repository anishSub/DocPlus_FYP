from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
class AdminOverviewView(TemplateView):
    template_name = 'superAdmin/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context

class UserManagementView(TemplateView):
    template_name = 'superAdmin/userManagement.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context
      
class HospitalsView(TemplateView):
    template_name = 'superAdmin/hospitals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context
      
class VerifyDoctorView(TemplateView):
    template_name = 'superAdmin/verifyDoctor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context