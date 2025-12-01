from django.shortcuts import render
from django.views.generic import TemplateView

# Option 1: The "Class-Based" way (Best for static dashboards)
class DoctorAdminOverview(TemplateView):
    template_name = 'doctorAdmin/overview.html'

    # If you need to pass data (like patient counts) later, you override this:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here
        # context['total_patients'] = 1247
        return context
      
class DoctorAdminAppointments(TemplateView):
    template_name = 'doctorAdmin/appointments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context
      
class PatientsListView(TemplateView):
    template_name = 'doctorAdmin/patients.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context
      
class DoctorScheduleView(TemplateView):
    template_name = 'doctorAdmin/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data 
      
class HospitalView(TemplateView):
    template_name = 'doctorAdmin/hospitals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context
      
class DoctorEarningsView(TemplateView):
    template_name = 'doctorAdmin/earnings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context
      
class DoctorRatingsView(TemplateView):
    template_name = 'doctorAdmin/ratings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context