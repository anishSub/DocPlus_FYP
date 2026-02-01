from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from datetime import date
from django.http import JsonResponse
from django.db.models import Q
from accounts.models import PatientProfile
from .forms import UserUpdateForm, PatientProfileUpdateForm
from appointments.models import Appointment
from find_doctor.models import DoctorProfile
from find_hospital.models import Hospital


# Create your views here.
class HomeView(View):
    def get(self, request):
        return render(request, 'home/home.html')
    
class AboutUsView(View):
    def get(self, request):
        return render(request, 'about_us/about_us.html')
    
class ContactUsView(View):
    def get(self, request):
        return render(request, 'contact_us/contact_us.html')



# --- 1. VIEW PROFILE (Dashboard) ---
class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        today = date.today()
        
        # Ensure Profile Exists
        profile, created = PatientProfile.objects.get_or_create(user=user)

        # A. Appointments Logic
        # 1. Upcoming (Scheduled & Future)
        upcoming_appt = Appointment.objects.filter(
            user=user, 
            status='scheduled',
            date__gte=today
        ).order_by('date', 'start_time').first()

        # 2. Recent History
        recent_appts = Appointment.objects.filter(user=user).exclude(
            id=upcoming_appt.id if upcoming_appt else None
        ).order_by('-date')[:5]

        # B. Stats
        total_appts = Appointment.objects.filter(user=user).count()
        
        context = {
            'user': user,
            'profile': profile,
            'upcoming_appt': upcoming_appt,
            'recent_appts': recent_appts,
            'total_appts': total_appts,
        }
        return render(request, 'profile_view/profile_view.html', context)

# --- 2. EDIT PROFILE ---
class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        # Pre-fill forms with current data
        u_form = UserUpdateForm(instance=request.user)
        p_form = PatientProfileUpdateForm(instance=request.user.patient_profile)
        
        context = {
            'u_form': u_form,
            'p_form': p_form
        }
        return render(request, 'profile_view/edit_profile.html', context)

    def post(self, request):
        # Process submitted data
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = PatientProfileUpdateForm(request.POST, request.FILES, instance=request.user.patient_profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile') # Make sure this URL name matches urls.py
            
        # If invalid, re-render with errors
        context = {
            'u_form': u_form,
            'p_form': p_form
        }
        return render(request, 'profile_view/edit_profile.html', context)
# --- 3. GLOBAL SEARCH API ---
class GlobalSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return JsonResponse({'doctors': [], 'hospitals': []})

        # 1. Search Doctors (Name, Specialty)
        doctors = DoctorProfile.objects.filter(
            Q(user__first_name__icontains=query) | 
            Q(user__last_name__icontains=query) | 
            Q(specialization__icontains=query)
        )[:3] # Limit to Top 3

        doctor_results = []
        for doc in doctors:
            doctor_results.append({
                'id': doc.id,
                'name': str(doc),
                'specialty': doc.specialization,
                'image': doc.profile_photo.url if doc.profile_photo else None,
                'url': f"/find_doctor/{doc.id}/" # Assuming this URL structure, need to verify
            })

        # 2. Search Hospitals (Name, City, Address)
        hospitals = Hospital.objects.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query)
        )[:3] # Limit to Top 3

        hospital_results = []
        for hosp in hospitals:
            hospital_results.append({
                'id': hosp.id,
                'name': hosp.name,
                'city': hosp.city,
                'image': hosp.image.url if hosp.image else None,
                'url': f"/find_hospital/hospital-details/{hosp.id}/" # Verified from urls.py
            })

        return JsonResponse({
            'doctors': doctor_results,
            'hospitals': hospital_results
        })
