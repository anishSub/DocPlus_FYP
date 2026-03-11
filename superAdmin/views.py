from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from find_doctor.models import DoctorProfile, DoctorReview
from find_hospital.models import Hospital, HospitalReview
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Sum
from appointments.models import Appointment
from .models import PlatformSettings
from accounts.models import Hospital


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
        
        today = timezone.now().date()
        
        context['total_appointments_today'] = Appointment.objects.filter(date=today).count()
        
        context['completed_appointments_count'] = Appointment.objects.filter(
            date=today, 
            status='completed'
        ).count()

        # --- 3. Revenue Stats ---
        revenue_data = Appointment.objects.filter(status='completed').aggregate(Sum('amount'))
        context['total_revenue'] = revenue_data['amount__sum'] or 0

        # --- 4. Pending Approvals ---
        context['pending_doctors'] = DoctorProfile.objects.filter(is_approved=False).select_related('user')[:5]
        context['pending_doctors_count'] = DoctorProfile.objects.filter(is_approved=False).count()
        
        # --- 5. Hospital Stats ---
        context['total_hospitals'] = Hospital.objects.count()
        context['pending_hospitals'] = Hospital.objects.filter(is_approved=False)[:5]
        context['pending_hospitals_count'] = Hospital.objects.filter(is_approved=False).count()
        

        recent_appointments = Appointment.objects.all().order_by('-date', '-start_time')[:5]
        
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

        # Search logic
        search_query = self.request.GET.get('q')
        hospitals = Hospital.objects.all().order_by('-created_at')
        if search_query:
            hospitals = hospitals.filter(
                Q(name__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(district__icontains=search_query)
            )

        # Separate pending (unverified) vs approved hospitals
        context['pending_hospitals'] = hospitals.filter(is_verified=False)
        context['pending_count'] = context['pending_hospitals'].count()
        context['approved_hospitals'] = hospitals.filter(is_verified=True)
        context['total_hospitals'] = Hospital.objects.count()
        context['search_query'] = search_query or ''

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


def approve_hospital(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    hospital.is_verified = True
    hospital.save()
    messages.success(request, f"'{hospital.name}' has been approved.")
    return redirect('super_admin_hospitals')

def reject_hospital(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    name = hospital.name
    hospital.delete()
    messages.error(request, f"'{name}' has been rejected and removed.")
    return redirect('super_admin_hospitals')

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

        doctor_reviews = DoctorReview.objects.all().select_related('user', 'doctor__user').order_by('-created_at')
        hospital_reviews = HospitalReview.objects.all().select_related('user', 'hospital').order_by('-created_at')

        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            doctor_reviews = doctor_reviews.filter(
                Q(user__first_name__icontains=search_query) |
                Q(doctor__user__first_name__icontains=search_query) |
                Q(comment__icontains=search_query)
            )
            hospital_reviews = hospital_reviews.filter(
                Q(user__first_name__icontains=search_query) |
                Q(hospital__name__icontains=search_query) |
                Q(comment__icontains=search_query)
            )

        context['doctor_reviews'] = doctor_reviews
        context['hospital_reviews'] = hospital_reviews
        context['pending_doctor_reviews'] = doctor_reviews.filter(is_approved=False).count()
        context['pending_hospital_reviews'] = hospital_reviews.filter(is_approved=False).count()
        context['flagged_count'] = context['pending_doctor_reviews'] + context['pending_hospital_reviews']
        context['search_query'] = search_query or ''

        return context


def approve_review(request, review_type, pk):
    if review_type == 'doctor':
        review = get_object_or_404(DoctorReview, pk=pk)
    else:
        review = get_object_or_404(HospitalReview, pk=pk)
    review.is_approved = True
    review.save()
    messages.success(request, "Review has been approved.")
    return redirect('super_admin_verify_reviews')

def reject_review(request, review_type, pk):
    if review_type == 'doctor':
        review = get_object_or_404(DoctorReview, pk=pk)
    else:
        review = get_object_or_404(HospitalReview, pk=pk)
    review.delete()
    messages.error(request, "Review has been rejected and removed.")
    return redirect('super_admin_verify_reviews')
    
class AnalyticsView(TemplateView):
    template_name = 'superAdmin/analytics.html'

    def get_context_data(self, **kwargs):
        import json
        from datetime import timedelta
        from django.db.models import Count, Avg
        from django.db.models.functions import TruncMonth
        from find_hospital.models import Hospital
        from find_doctor.models import DoctorReview

        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # ── 1. Revenue metrics (real data) ──
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        revenue_today = Appointment.objects.filter(
            status='completed', date=today
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        revenue_week = Appointment.objects.filter(
            status='completed', date__gte=week_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        revenue_month = Appointment.objects.filter(
            status='completed', date__gte=month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        revenue_total = Appointment.objects.filter(
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        context['revenue_today'] = revenue_today
        context['revenue_week'] = revenue_week
        context['revenue_month'] = revenue_month
        context['revenue_total'] = revenue_total

        # ── 2. User activity metrics (real data) ──
        context['active_today'] = User.objects.filter(last_login__date=today).count()
        context['new_signups_today'] = User.objects.filter(date_joined__date=today).count()
        context['total_users'] = User.objects.count()

        # ── 3. Appointment metrics (real data) ──
        total_appts = Appointment.objects.count()
        completed_count = Appointment.objects.filter(status='completed').count()
        cancelled_count = Appointment.objects.filter(status='cancelled').count()
        completion_rate = round((completed_count / total_appts * 100), 1) if total_appts else 0
        cancellation_rate = round((cancelled_count / total_appts * 100), 1) if total_appts else 0

        # Average doctor rating
        avg_rating = DoctorReview.objects.aggregate(Avg('rating'))['rating__avg']
        avg_rating = round(avg_rating, 1) if avg_rating else 0

        context['completion_rate'] = completion_rate
        context['cancellation_rate'] = cancellation_rate
        context['avg_rating'] = avg_rating

        # ══════════════ CHART DATA ══════════════

        # Chart 1 – User Role Distribution (Doughnut)
        role_counts = list(
            User.objects.values('role')
            .annotate(count=Count('id'))
            .order_by('role')
        )
        context['chart_user_roles'] = json.dumps(
            {item['role']: item['count'] for item in role_counts}
        )

        # Chart 2 – Appointment Status Breakdown (Doughnut)
        status_counts = list(
            Appointment.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )
        context['chart_appt_status'] = json.dumps(
            {item['status'].capitalize(): item['count'] for item in status_counts}
        )

        # Chart 3 – Hospital Type Distribution (Doughnut)
        hospital_types = list(
            Hospital.objects.values('hospital_type')
            .annotate(count=Count('id'))
            .order_by('hospital_type')
        )
        context['chart_hospital_types'] = json.dumps(
            {item['hospital_type']: item['count'] for item in hospital_types}
        )

        # Chart 4 – Top Doctor Specializations (Horizontal Bar)
        spec_counts = list(
            DoctorProfile.objects.values('specialization')
            .annotate(count=Count('id'))
            .order_by('-count')[:8]
        )
        context['chart_specializations'] = json.dumps(
            {item['specialization']: item['count'] for item in spec_counts}
        )

        # Chart 5 – Monthly Appointments (last 6 months, Vertical Bar)
        six_months_ago = today - timedelta(days=180)
        monthly_appts = list(
            Appointment.objects.filter(date__gte=six_months_ago)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        context['chart_monthly_appts'] = json.dumps(
            {item['month'].strftime('%b %Y'): item['count'] for item in monthly_appts}
        )

        # Chart 6 – Revenue by Month (last 6 months, Vertical Bar)
        monthly_rev = list(
            Appointment.objects.filter(date__gte=six_months_ago, status='completed')
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        context['chart_monthly_revenue'] = json.dumps(
            {item['month'].strftime('%b %Y'): float(item['total']) for item in monthly_rev}
        )

        return context
    
class SettingsView(TemplateView):
    template_name = 'superAdmin/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['platform_settings'] = PlatformSettings.load()
        return context

    def post(self, request, *args, **kwargs):
        settings_obj = PlatformSettings.load()
        settings_obj.maintenance_mode = 'maintenance_mode' in request.POST
        settings_obj.allow_registration = 'allow_registration' in request.POST
        settings_obj.auto_approve_reviews = 'auto_approve_reviews' in request.POST
        settings_obj.email_notifications = 'email_notifications' in request.POST
        settings_obj.save()
        messages.success(request, "Settings saved successfully.")
        return redirect('super_admin_settings')

from .models import ErrorLog
from django.views.generic import ListView, DetailView

class ErrorLogListView(ListView):
    model = ErrorLog
    template_name = 'superAdmin/error_logs.html'
    context_object_name = 'errors'
    ordering = ['-timestamp']
    paginate_by = 20

class ErrorLogDetailView(DetailView):
    model = ErrorLog
    template_name = 'superAdmin/error_log_detail.html'
    context_object_name = 'error'
