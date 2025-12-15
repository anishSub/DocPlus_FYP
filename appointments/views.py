from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import Appointment
from find_doctor.models import DoctorProfile
from datetime import datetime, timedelta 

class AppointmentView(View):
    def get(self, request):
        # 1. Fetch approved doctors for dropdown
        doctors = DoctorProfile.objects.filter(is_approved=True).select_related('user')
        
        # 2. CAPTURE PRE-FILLED DATA (From URL Parameters)
        pre_doctor_id = request.GET.get('doctor')
        pre_date = request.GET.get('appointment_date')
        pre_time = request.GET.get('time_slot')
        
        # Safe conversion of ID to integer for template comparison
        try:
            pre_doctor_id = int(pre_doctor_id) if pre_doctor_id else None
        except ValueError:
            pre_doctor_id = None

        context = {
            'doctors': doctors,
            'pre_doctor_id': pre_doctor_id,
            'pre_date': pre_date,
            'pre_time': pre_time,
        }
        return render(request, 'appointment/appointment.html', context)


@require_POST
def save_appointment(request):
    # --- 1. Extract Data ---
    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    dob = request.POST.get('dob')
    gender = request.POST.get('gender')
    city = request.POST.get('city')
    address = request.POST.get('address')

    doctor_id = request.POST.get('doctor') 
    doctor_obj = get_object_or_404(DoctorProfile, id=doctor_id)
    doctor_name_str = f"Dr. {doctor_obj.user.first_name} {doctor_obj.user.last_name}"
    
    appointment_date = request.POST.get('appointment_date')
    
    # --- 2. TIME CONVERSION LOGIC ---
    time_str = request.POST.get('time_slot') # Gets "09:00 AM" string
    
    start_time_obj = None
    end_time_obj = None

    try:
        # Parse the string "09:00 AM" -> Python Time Object
        start_datetime = datetime.strptime(time_str, "%I:%M %p") 
        start_time_obj = start_datetime.time()
        
        # Calculate End Time (Adding 30 minutes duration)
        end_datetime = start_datetime + timedelta(minutes=30)
        end_time_obj = end_datetime.time()
    except (ValueError, TypeError):
        # Redirect back if time is missing/invalid
        return redirect('appointment_page') 

    reason = request.POST.get('reason')
    symptoms = request.POST.get('symptoms')
    medical_reports = request.FILES.get('medical_reports')
    payment_method = request.POST.get('payment_method')

    # --- 3. SAVE TO DATABASE ---
    appointment = Appointment.objects.create(
        user=request.user if request.user.is_authenticated else None,
        full_name=full_name,
        email=email,
        phone=phone,
        dob=dob,
        gender=gender,
        city=city,
        address=address,
        doctor=doctor_obj, 
        date=appointment_date,
        
        start_time=start_time_obj, 
        end_time=end_time_obj,
        
        reason=reason,
        symptoms=symptoms,
        medical_reports=medical_reports,
        payment_method=payment_method,
        status='scheduled',
        amount=doctor_obj.consultation_fee 
    )
    
    context = {
        'patient_name': full_name,
        'doctor_name': doctor_name_str,
        'date': appointment_date,
        'time': time_str, 
        'fee': f"NPR {doctor_obj.consultation_fee}",
        'email': email,
        'payment_method': payment_method
    }
    
    return render(request, 'appointment/appointment_success.html', context)