from django.shortcuts import get_object_or_404, render
from django.views.generic import UpdateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from find_hospital.models import Hospital
from .forms import HospitalUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, F
from find_hospital.models import Hospital, HospitalReview
from find_doctor.models import DoctorProfile



class HospitalAdminOverview(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'  # Change this to your actual login url name

    def test_func(self):
        # Verify user is a HOSPITAL_ADMIN and has a linked profile
        return self.request.user.role == 'HOSPITAL_ADMIN' and hasattr(self.request.user, 'hospital_profile')

    def handle_no_permission(self):
        # Redirect unauthorized users
        messages.error(self.request, "You are not authorized to view this page.")
        return redirect('/') 

    def get(self, request):
        hospital = request.user.hospital_profile
        
        # --- 1. Analytics Data ---
        views = hospital.total_views
        clicks = hospital.total_website_clicks
        
        # Calculate Conversion Rate (Clicks / Views)
        conversion_rate = round((clicks / views * 100), 1) if views > 0 else 0

        # --- 2. Other Real Data ---
        total_beds = hospital.total_beds
        
        # Doctors: Count only approved doctors linked to this hospital
        active_doctors_count = DoctorProfile.objects.filter(
            hospital_affiliation=hospital, is_approved=True
        ).count()

        # Reviews: Get total count and average rating
        reviews_qs = HospitalReview.objects.filter(hospital=hospital)
        total_reviews = reviews_qs.count()
        avg_rating_data = reviews_qs.aggregate(Avg('rating'))
        avg_rating = avg_rating_data['rating__avg'] if avg_rating_data['rating__avg'] else 0.0

        context = {
            'hospital': hospital,
            'stats': {
                'views': views,
                'clicks': clicks,
                'conversion_rate': conversion_rate,
                'total_reviews': total_reviews,
                'avg_rating': round(avg_rating, 1),
                'active_doctors': active_doctors_count,
            },
            'performance': {
                'total_beds': total_beds,
                # Simulating 65% occupancy for visual demo purposes since specific patient admission logic isn't built yet
                'occupied_beds': int(total_beds * 0.65), 
            }
        }
        return render(request, 'find_hospital/dashboard/overview.html', context)




class HospitalDoctorManagementView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/' # Update with your login URL

    def test_func(self):
        # Ensure user is Hospital Admin
        return self.request.user.role == 'HOSPITAL_ADMIN' and hasattr(self.request.user, 'hospital_profile')

    def get(self, request):
        hospital = request.user.hospital_profile
        
        # Fetch all approved doctors linked to this hospital
        doctors = DoctorProfile.objects.filter(
            hospital_affiliation=hospital,
            is_approved=True 
        ).select_related('user') # Optimize query
        
        context = {
            'hospital': hospital,
            'doctors': doctors,
            'doctor_count': doctors.count()
        }
        return render(request, 'find_hospital/dashboard/doctor_management.html', context)

    def post(self, request):
        # Handle "Remove Doctor" action
        doctor_id = request.POST.get('doctor_id')
        action = request.POST.get('action')

        if action == 'remove' and doctor_id:
            try:
                doctor = get_object_or_404(DoctorProfile, id=doctor_id)
                
                # Security Check: Ensure this doctor actually belongs to THIS hospital
                if doctor.hospital_affiliation == request.user.hospital_profile:
                    doctor.hospital_affiliation = None # Unlink them
                    doctor.save()
                    messages.success(request, f"Dr. {doctor.user.first_name} removed successfully.")
                else:
                    messages.error(request, "Unauthorized action.")
            except Exception as e:
                messages.error(request, "Something went wrong.")
        
        return redirect('hospital_doctor_management')
    
    
    
class HospitalEditView(LoginRequiredMixin, UpdateView):
    model = Hospital
    form_class = HospitalUpdateForm
    template_name = 'hospitalAdmin/edit_hospital.html'
    success_url = reverse_lazy('hospital_admin_overview') 

    def get_object(self, queryset=None):
        return self.request.user.hospital_profile

    def form_valid(self, form):
        messages.success(self.request, "Hospital profile updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error updating profile. Please check the form.")
        return super().form_invalid(form)