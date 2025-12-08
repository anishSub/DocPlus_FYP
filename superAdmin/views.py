from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from find_doctor.models import DoctorProfile
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q,Sum
from appointments.models import Appointment


User = get_user_model()
# Create your views here.
class AdminOverviewView(TemplateView):
    template_name = 'superAdmin/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # --- 1. User Stats ---
        context['total_users'] = User.objects.count()
        context['total_patients'] = User.objects.filter(role='PATIENT').count()
        context['total_doctors'] = User.objects.filter(role='DOCTOR').count()
        
        # --- 2. Appointment Stats ---
        today = timezone.now().date()
        
        # FIX: Using 'date' instead of 'appointment_date'
        context['total_appointments_today'] = Appointment.objects.filter(date=today).count()
        
        # FIX: Using lowercase 'completed' based on your model choices
        context['completed_appointments_count'] = Appointment.objects.filter(
            date=today, 
            status='completed'
        ).count()

        # --- 3. Revenue Stats ---
        # Calculate total revenue from completed appointments
        revenue_data = Appointment.objects.filter(status='completed').aggregate(Sum('amount'))
        context['total_revenue'] = revenue_data['amount__sum'] or 0

        # --- 4. Pending Approvals ---
        context['pending_doctors'] = DoctorProfile.objects.filter(is_approved=False).select_related('user')[:5]
        context['pending_doctors_count'] = DoctorProfile.objects.filter(is_approved=False).count()
        
        # (Placeholder for hospitals if you have that model)
        # context['pending_hospitals_count'] = Hospital.objects.filter(is_approved=False).count()

        # --- 5. RECENT APPOINTMENTS (THE FIX) ---
        # CRITICAL FIX: 
        # 1. Used 'date' instead of 'appointment_date' in order_by
        # 2. Removed select_related('doctor') because your model uses 'doctor_name' (CharField), not a ForeignKey
        recent_appointments = Appointment.objects.all().order_by('-date', '-time_slot')[:5]
        
        context['recent_appointments'] = recent_appointments

        return context



    




class UserManagementView(TemplateView):
    template_name = 'superAdmin/userManagement.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Base Query: Get all users, ordered by newest first and exclude superuser so you dont delete 
        users = User.objects.filter(is_superuser=False).order_by('-date_joined')
        # 2. Search Logic
        search_query = self.request.GET.get('q')
        if search_query:
            users = users.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(email__icontains=search_query)
            )

        # 3. Calculate Stats using 'role' field
        # UPDATED: Using UPPERCASE strings to match your User model
        total_patients = User.objects.filter(role='PATIENT').count()
        total_doctors = User.objects.filter(role='DOCTOR').count()
        
        today = timezone.now().date()
        active_today = User.objects.filter(last_login__date=today).count()

        context['users'] = users
        context['total_patients'] = total_patients
        context['total_doctors'] = total_doctors
        context['active_today'] = active_today
        
        return context




class HospitalsView(TemplateView):
    template_name = 'superAdmin/hospitals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context



class VerifyDoctorView(TemplateView):
    template_name = 'superAdmin/verifyDoctor.html'

    def get(self, request):
        # Fetch only doctors who are NOT approved yet
        pending_doctors = DoctorProfile.objects.filter(is_approved=False).select_related('user')
        
        context = {
            'doctors': pending_doctors,
            'pending_count': pending_doctors.count()
        }
        return render(request, self.template_name, context)

# --- Action Views (Function-based is easier here) ---

def approve_doctor(request, pk):
    # Get the specific doctor profile by ID (pk)
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    
    # Update status
    doctor.is_approved = True
    doctor.save()
    
    messages.success(request, f"Dr. {doctor.user.first_name} has been approved and activated.")
    return redirect('super_admin_verify_doctor')

def reject_doctor(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    user = doctor.user
    
    # Store name for the message before deleting
    name = user.first_name
    
    # Delete the USER (this cascades and deletes the Profile too)
    user.delete()
    
    messages.error(request, f"Application for Dr. {name} has been rejected and removed.")
    return redirect('super_admin_verify_doctor')

def delete_user(request, pk):
    # Get the user or show 404
    user_to_delete = get_object_or_404(User, pk=pk)
    
    # Optional safety: Prevent deleting Superusers/Admins
    if user_to_delete.is_superuser:
        messages.error(request, "You cannot delete a Super Admin account.")
        return redirect('user_management') # Ensure this matches your URL name for the list page

    name = user_to_delete.first_name or user_to_delete.email
    
    # Delete the user
    user_to_delete.delete()
    
    messages.success(request, f"User '{name}' has been successfully removed.")
    return redirect('super_admin_users') 

#*Appointment Verification View
class VerifyAppointmentView(TemplateView):
    template_name = 'superAdmin/appointment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Get all appointments (newest first)
        appointments = Appointment.objects.all().order_by('-date', '-created_at')

        # 2. Search Logic (Search by Patient Name, Doctor Name, or Status)
        search_query = self.request.GET.get('q')
        if search_query:
            appointments = appointments.filter(
                Q(full_name__icontains=search_query) | 
                Q(doctor_name__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        context['appointments'] = appointments
        return context
    
    

class VerifyReviewsView(TemplateView):
    template_name = 'superAdmin/review.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context
    
class AnalyticsView(TemplateView):
    template_name = 'superAdmin/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context
    
class SettingsView(TemplateView):
    template_name = 'superAdmin/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context data here if needed
        return context
    
