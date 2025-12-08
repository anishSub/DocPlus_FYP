from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import DoctorProfileUpdateForm
from find_doctor.models import DoctorProfile

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
    



@login_required
def edit_doctor_profile(request):
    try:
        # Get the logged-in doctor's profile
        doctor_profile = request.user.doctor_profile
    except DoctorProfile.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('home')

    if request.method == 'POST':
        # UPDATE existing data
        # 'request.FILES' is crucial for image uploads
        form = DoctorProfileUpdateForm(request.POST, request.FILES, instance=doctor_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            # Fixed Redirect: Must match the name in urls.py
            return redirect('edit_profile') 
    else:
        # PRE-FILL form with existing data
        form = DoctorProfileUpdateForm(instance=doctor_profile)

    context = {
        'form': form,
        'doctor': doctor_profile
    }
    return render(request, 'doctorAdmin/edit_profile.html', context)
