from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from datetime import date
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import EmailMessage, BadHeaderError
from django.conf import settings
from accounts.models import PatientProfile
from .forms import UserUpdateForm, PatientProfileUpdateForm
from appointments.models import Appointment
from find_doctor.models import DoctorProfile
from find_hospital.models import Hospital


from .models import PlatformTestimonial
from .forms import PlatformTestimonialForm

# Create your views here.
class HomeView(View):
    def get(self, request):
        # Fetch up to 3 approved testimonials
        testimonials = PlatformTestimonial.objects.filter(is_approved=True).select_related('user')[:3]
        return render(request, 'home/home.html', {'testimonials': testimonials})
    
class AboutUsView(View):
    def get(self, request):
        form = PlatformTestimonialForm()
        return render(request, 'about_us/about_us.html', {'form': form})
        
    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to submit a review.')
            return redirect('login')
            
        form = PlatformTestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user
            testimonial.save()
            messages.success(request, 'Thank you! Your review has been submitted and is pending approval.')
            return redirect('about_us')
            
        messages.error(request, 'Please correct the errors below.')
        return render(request, 'about_us/about_us.html', {'form': form})
    
class ContactUsView(View):
    def get(self, request):
        return render(request, 'contact_us/contact_us.html')

    def post(self, request):
        full_name = request.POST.get('full_name', '').strip()
        email     = request.POST.get('email', '').strip()
        phone     = request.POST.get('phone', '').strip()
        subject   = request.POST.get('subject', '').strip()
        message   = request.POST.get('message', '').strip()

        # Basic validation
        if not all([full_name, email, subject, message]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'contact_us/contact_us.html')

        email_subject = f"[DocPlus Contact] {subject} — from {full_name}"
        email_body = f"""You have a new message via the DocPlus Contact Us form.

From:    {full_name}
Email:   {email}
Phone:   {phone or 'Not provided'}
Subject: {subject}

Message:
{message}

---
Reply directly to this email to respond to {full_name}.
"""

        try:
            msg = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.EMAIL_HOST_USER],
                reply_to=[email],
            )
            msg.send(fail_silently=False)
            messages.success(
                request,
                f'✅ Thank you, {full_name}! Your message has been sent. We\'ll get back to you soon.'
            )
        except BadHeaderError:
            messages.error(request, 'Invalid header found. Please check your inputs.')
        except Exception:
            messages.error(
                request,
                '❌ Sorry, we could not send your message right now. Please try again later or call us directly.'
            )

        return redirect('contact_us')



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
        
        # C. Saved Doctors
        favorite_doctors = profile.favorite_doctors.all() if profile.favorite_doctors.exists() else []

        context = {
            'user': user,
            'profile': profile,
            'upcoming_appt': upcoming_appt,
            'recent_appts': recent_appts,
            'total_appts': total_appts,
            'favorite_doctors': favorite_doctors,
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
            'hospitals': hospital_results
        })

# --- 4. TOGGLE FAVORITE DOCTOR (AJAX) ---
class ToggleFavoriteDoctorView(View):
    def post(self, request, doctor_id):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'You must be logged in as a patient to save a doctor.'}, status=401)
            
        if not hasattr(request.user, 'patient_profile'):
            return JsonResponse({'status': 'error', 'message': 'Only patients can save doctors.'}, status=403)
            
        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        profile = request.user.patient_profile
        
        if profile.favorite_doctors.filter(id=doctor.id).exists():
            profile.favorite_doctors.remove(doctor)
            is_favorite = False
        else:
            profile.favorite_doctors.add(doctor)
            is_favorite = True
            
        return JsonResponse({'status': 'success', 'is_favorite': is_favorite})

# --- 5. TOGGLE FAVORITE HOSPITAL (AJAX) ---
class ToggleFavoriteHospitalView(View):
    def post(self, request, hospital_id):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'You must be logged in as a patient to save a hospital.'}, status=401)
            
        if not hasattr(request.user, 'patient_profile'):
            return JsonResponse({'status': 'error', 'message': 'Only patients can save hospitals.'}, status=403)
        
        from find_hospital.models import Hospital
        hospital = get_object_or_404(Hospital, id=hospital_id)
        profile = request.user.patient_profile
        
        if profile.favorite_hospitals.filter(id=hospital.id).exists():
            profile.favorite_hospitals.remove(hospital)
            is_favorite = False
        else:
            profile.favorite_hospitals.add(hospital)
            is_favorite = True
            
        return JsonResponse({'status': 'success', 'is_favorite': is_favorite})
