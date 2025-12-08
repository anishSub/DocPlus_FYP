from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from .models import Appointment
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from .models import Appointment
from find_doctor.models import DoctorProfile


class AppointmentView(View):
    # Handle viewing the page (GET request)
    def get(self, request):
        # Fetch approved doctors to populate the select dropdown
        doctors = DoctorProfile.objects.filter(is_approved=True).select_related('user')
        
        context = {
            'doctors': doctors
        }
        return render(request, 'appointment/appointment.html', context)

@require_POST
def save_appointment(request):
    # --- 1. Extract Data from Step 1 (Personal) ---
    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    dob = request.POST.get('dob')
    gender = request.POST.get('gender')
    city = request.POST.get('city')
    address = request.POST.get('address')

    # --- 2. Extract Data from Step 2 (Appointment) ---
    # The HTML select returns the Doctor's ID (value="{{ doctor.id }}")
    doctor_id = request.POST.get('doctor') 
    
    # We fetch the actual object to get the Name and Fee
    doctor_obj = get_object_or_404(DoctorProfile, id=doctor_id)
    doctor_name_str = f"Dr. {doctor_obj.user.first_name} {doctor_obj.user.last_name}"
    doctor_fee = doctor_obj.consultation_fee

    appointment_date = request.POST.get('appointment_date')
    time_slot = request.POST.get('time_slot')

    # --- 3. Extract Data from Step 3 (Medical) ---
    reason = request.POST.get('reason')
    symptoms = request.POST.get('symptoms')
    
    # Handle File Upload (Medical Reports)
    medical_reports = request.FILES.get('medical_reports')

    # --- 4. Extract Data from Step 4 (Payment) ---
    payment_method = request.POST.get('payment_method')

    # --- 5. SAVE TO DATABASE ---
    appointment = Appointment.objects.create(
        user=request.user if request.user.is_authenticated else None, # Handle guest users if needed
        full_name=full_name,
        email=email,
        phone=phone,
        dob=dob,
        gender=gender,
        city=city,
        address=address,
        doctor_name=doctor_name_str, # Save the readable name, not the ID
        date=appointment_date,
        time_slot=time_slot,
        reason=reason,
        symptoms=symptoms,
        medical_reports=medical_reports,
        payment_method=payment_method,
        status='scheduled' 
    )
    
    # --- 6. Prepare Success Page Data ---
    context = {
        'patient_name': full_name,
        'doctor_name': doctor_name_str,
        'date': appointment_date,
        'time': time_slot,
        'fee': f"NPR {doctor_fee}", # Use the real fee from database
        'email': email,
        'payment_method': payment_method
    }
    
    # Render the success page directly
    return render(request, 'appointment/appointment_success.html', context)