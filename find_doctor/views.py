from django.shortcuts import render, redirect
from django.views import View
from .forms import DoctorRegistrationForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView

# Create your views here.
class FindDoctorView(View):
    def get(self, request):
        return render(request, 'find_doctor/find_doctor.html')
    
    
class DcotorDetailsView(View):
    def get(self, request):
        return render(request, 'find_doctor/doctor_detail.html')

# find_doctor/views.py

class DoctorRegistrationView(View):
    template_name = 'find_doctor/doctor_registration.html'

    def get(self, request):
        form = DoctorRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # Ensure request.FILES is passed for file uploads
        form = DoctorRegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                form.save()
                return redirect('registration_success') 
            except Exception as e:
                print(f"--- SYSTEM ERROR: {e} ---") # Print system errors
                messages.error(request, f"System Error: {e}")
        else:
            # --- ADD THIS BLOCK TO SEE WHY IT FAILS ---
            print("\n" + "="*30)
            print("❌ FORM VALIDATION FAILED!")
            print(form.errors)  # <--- THIS WILL TELL YOU THE REASON
            print("="*30 + "\n")
            # ------------------------------------------
            messages.error(request, "Registration failed. Check errors.")
            
        return render(request, self.template_name, {'form': form})


def check_email(request):
    email = request.GET.get('email', None)
    response = {
        'exists': False
    }
    if email:
        User = get_user_model()
        # Check if ANY user exists with this email
        if User.objects.filter(email__iexact=email).exists():
            response['exists'] = True
            
    return JsonResponse(response)

    
class RegistrationSuccessView(View):
    def get(self, request):
        return render(request, 'find_doctor/registration_success.html')