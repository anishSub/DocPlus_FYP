
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import DoctorProfileUpdateForm
from django.http import JsonResponse
import json
from django.views.decorators.http import require_http_methods
from find_doctor.models import DoctorSchedule, DoctorProfile
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Avg, Count
from datetime import date,timedelta
from appointments.models import Appointment
from find_doctor.models import DoctorReview



class DoctorAdminOverview(LoginRequiredMixin, TemplateView):
    template_name = 'doctorAdmin/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Get the Logged-in Doctor
        if not hasattr(self.request.user, 'doctor_profile'):
            return context # Prevent crash if admin/patient logs in
            
        doctor = self.request.user.doctor_profile
        today = date.today()

        # --- A. CALCULATE STATS ---
        
        # 1. Total Patients (Count unique users who booked this doctor)
        total_patients = Appointment.objects.filter(doctor=doctor).values('user').distinct().count()
        
        # 2. Appointments Today
        appointments_today_qs = Appointment.objects.filter(doctor=doctor, date=today).order_by('start_time')
        count_today = appointments_today_qs.count()
        
        # 3. Monthly Earnings (Sum of amount for 'completed' appointments this month)
        monthly_earnings = Appointment.objects.filter(
            doctor=doctor, 
            status='completed', 
            date__month=today.month,
            date__year=today.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # 4. Average Rating
        avg_rating = DoctorReview.objects.filter(doctor=doctor).aggregate(Avg('rating'))['rating__avg'] or 0.0

        # --- B. FETCH LISTS ---
        
        # 1. Today's Appointments (Limit to 5)
        context['appointments_today'] = appointments_today_qs[:5]
        
        # 2. Recent Patients (Last 5 unique appointments)
        # Note: True "distinct" on fields is Postgres only. This is a generic safe way:
        recent_appointments = Appointment.objects.filter(doctor=doctor).order_by('-date', '-start_time')[:5]
        
        # 3. Latest Reviews
        latest_reviews = DoctorReview.objects.filter(doctor=doctor).order_by('-created_at')[:3]

        # --- C. PASS TO CONTEXT ---
        context.update({
            'total_patients': total_patients,
            'count_today': count_today,
            'monthly_earnings': monthly_earnings,
            'avg_rating': avg_rating,
            'recent_patients': recent_appointments, # Using appts as proxy for patients
            'latest_reviews': latest_reviews,
            'doctor': doctor
        })
        
        return context


class DoctorAdminAppointments(LoginRequiredMixin, TemplateView):
    template_name = 'doctorAdmin/appointments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Safety Check: Ensure user is a doctor
        if not hasattr(self.request.user, 'doctor_profile'):
            return context

        doctor = self.request.user.doctor_profile
        today = date.today()

        # 1. Fetch All Appointments for this Doctor
        # We order by date (descending) and time
        all_appointments = Appointment.objects.filter(doctor=doctor).order_by('-date', 'start_time')

        # 2. Filter: Upcoming (Scheduled & Today or Future)
        # Note: You can add logic for 'today' specifically if you want separate sections
        upcoming_appointments = all_appointments.filter(
            status='scheduled',
            date__gte=today
        ).order_by('date', 'start_time') # Ascending for upcoming (soonest first)

        # 3. Filter: Past (Completed, Cancelled, or Old Dates)
        past_appointments = all_appointments.exclude(id__in=upcoming_appointments)

        context.update({
            'upcoming_appointments': upcoming_appointments,
            'past_appointments': past_appointments,
            'today_count': upcoming_appointments.filter(date=today).count()
        })
        
        return context




class PatientsListView(LoginRequiredMixin, TemplateView):
    template_name = 'doctorAdmin/patients.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Safety Check
        if not hasattr(self.request.user, 'doctor_profile'):
            return context

        doctor = self.request.user.doctor_profile
        
        # 1. Fetch all appointments (Newest first)
        # We need newest first to grab the "Last Visit" date correctly
        appointments = Appointment.objects.filter(doctor=doctor).order_by('-date', '-start_time')
        
        patients_list = []
        seen_ids = set()
        
        # 2. Filter Unique Patients
        for appt in appointments:
            # Create a unique identifier (User ID preferred, else Phone for guests)
            identifier = appt.user.id if appt.user else appt.phone
            
            if identifier not in seen_ids:
                seen_ids.add(identifier)
                
                # Determine Status Logic
                status_label = "Active"
                status_class = "treatment" # CSS class
                
                if appt.status == 'cancelled':
                    status_label = "Inactive"
                    status_class = "recovered"
                elif appt.status == 'scheduled':
                    status_label = "Upcoming"
                    status_class = "new"

                # Add to list
                patients_list.append({
                    'name': appt.full_name,
                    'last_visit': appt.date,
                    'diagnosis': appt.reason, # Using 'Reason' as Diagnosis for now
                    'status': status_label,
                    'css_class': status_class,
                    'avatar_char': appt.full_name[0].upper() if appt.full_name else "?"
                })
        
        context['patients'] = patients_list
        context['total_count'] = len(patients_list)
        return context
    
    
    
    


class DoctorScheduleView(LoginRequiredMixin, TemplateView):
    template_name = 'doctorAdmin/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Safety Check
        if not hasattr(self.request.user, 'doctor_profile'):
            return context

        doctor = self.request.user.doctor_profile
        
        # 1. Fetch all schedules for this doctor
        schedules = DoctorSchedule.objects.filter(doctor=doctor)
        
        # 2. Organize data by Day for the Template
        # We define the order we want to show
        days_order = [
            ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
            ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')
        ]
        
        weekly_schedule = []
        
        for short_name, full_name in days_order:
            # Find slots for this specific day
            day_slots = schedules.filter(day=short_name).order_by('start_time')
            
            is_active = day_slots.exists()
            
            # Create a simplified string like "09:00 AM - 05:00 PM"
            # If multiple slots, we list them all
            time_display = []
            for slot in day_slots:
                start = slot.start_time.strftime("%I:%M %p")
                end = slot.end_time.strftime("%I:%M %p")
                time_display.append(f"{start} - {end}")
            
            weekly_schedule.append({
                'day': full_name,
                'short': short_name,
                'is_active': is_active,
                'times': time_display, # List of strings
                'slots': day_slots     # Actual objects if needed for ID
            })
            
        context['weekly_schedule'] = weekly_schedule
        return context
    
    
    


class HospitalView(LoginRequiredMixin, TemplateView):
    template_name = 'doctorAdmin/hospitals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Safety Check
        if hasattr(self.request.user, 'doctor_profile'):
            context['doctor'] = self.request.user.doctor_profile
            
        return context
    
    


class DoctorEarningsView(LoginRequiredMixin, TemplateView):
    template_name = 'doctorAdmin/earnings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Safety Check
        if not hasattr(self.request.user, 'doctor_profile'):
            return context

        doctor = self.request.user.doctor_profile
        today = date.today()

        # 1. Total Earnings (All time, Completed only)
        total_earnings = Appointment.objects.filter(
            doctor=doctor, 
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # 2. This Month Earnings
        this_month_earnings = Appointment.objects.filter(
            doctor=doctor, 
            status='completed',
            date__month=today.month,
            date__year=today.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # 3. Last Month Earnings
        # Calculate the previous month/year safely
        first_day_this_month = today.replace(day=1)
        last_month_date = first_day_this_month - timedelta(days=1)
        
        last_month_earnings = Appointment.objects.filter(
            doctor=doctor, 
            status='completed',
            date__month=last_month_date.month,
            date__year=last_month_date.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # 4. Recent Transactions (Table Data)
        # We show all appointments, but status helps differentiate paid/unpaid
        transactions = Appointment.objects.filter(doctor=doctor).order_by('-date')[:10]

        context.update({
            'total_earnings': total_earnings,
            'this_month_earnings': this_month_earnings,
            'last_month_earnings': last_month_earnings,
            'transactions': transactions
        })
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



# 1. GET Schedule (Fetch times for a specific day)
def get_schedule(request):
    day = request.GET.get('day')
    doctor = request.user.doctor_profile
    
    schedules = DoctorSchedule.objects.filter(doctor=doctor, day=day).values('id', 'start_time', 'end_time')
    return JsonResponse({'status': 'success', 'schedules': list(schedules)})

# 2. ADD Schedule (Create a new slot)
@require_http_methods(["POST"])
def add_schedule(request):
    try:
        data = json.loads(request.body)
        doctor = request.user.doctor_profile
        
        # Create the schedule
        schedule = DoctorSchedule.objects.create(
            doctor=doctor,
            day=data['day'],
            start_time=data['start_time'],
            end_time=data['end_time']
        )
        
        # --- SYNC: Automatically add this day to the Doctor's available_days list ---
        if data['day'] not in doctor.available_days:
            doctor.available_days.append(data['day'])
            doctor.save()

        return JsonResponse({'status': 'success', 'id': schedule.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

# 3. DELETE Schedule
@require_http_methods(["POST"])
def delete_schedule(request):
    data = json.loads(request.body)
    schedule_id = data.get('id')
    
    # Ensure the doctor owns this schedule before deleting
    schedule = get_object_or_404(DoctorSchedule, id=schedule_id, doctor=request.user.doctor_profile)
    day_removed = schedule.day
    schedule.delete()
    
    # --- SYNC: If no times left for this day, remove from available_days ---
    doctor = request.user.doctor_profile
    if not DoctorSchedule.objects.filter(doctor=doctor, day=day_removed).exists():
        if day_removed in doctor.available_days:
            doctor.available_days.remove(day_removed)
            doctor.save()

    return JsonResponse({'status': 'success'})