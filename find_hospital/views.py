from django.shortcuts import render, redirect
from django.views import View
from django.views import View
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Hospital

# Create your views here.
class FindHospitalView(View):
    def get(self, request):
        return render(request, 'find_hospital/find_hospital.html')
    
class HospitalDetailView(View):
    def get(self, request):
        return render(request, 'find_hospital/hospital_detail.html')
    

User = get_user_model()

class HospitalRegistrationView(View):
    def get(self, request):
        return render(request, 'find_hospital/hospital_registration.html')

    def post(self, request):
        try:
            data = request.POST
            files = request.FILES
            
            # --- 1. Password Validation ---
            password = data.get('password')
            password_confirm = data.get('password_confirm')
            email = data.get('email')

            if password != password_confirm:
                messages.error(request, "Passwords do not match.")
                return render(request, 'find_hospital/hospital_registration.html')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return render(request, 'find_hospital/hospital_registration.html')

            # --- 2. Create the User Account First ---
            # We use the email as the username
            user = User.objects.create_user(
                username=email, 
                email=email, 
                password=password,
                role=User.Role.HOSPITAL_ADMIN
            )

            services_list = request.POST.getlist('services') 
            services_str = ", ".join(services_list) 

            # Emergency (Checkbox -> Boolean)
            emergency_status = True if data.get('emergency_available') == 'on' else False
            
            # Departments (Hidden input "Dental,Ortho" -> List)
            dept_str = data.get('departments', '')
            dept_list = dept_str.split(',') if dept_str else []

            # --- 4. Create the Hospital Object (Linked to User) ---
            hospital = Hospital.objects.create(
                user=user,  # <--- LINKING THE NEW USER HERE
                name=data.get('name'),
                hospital_type=data.get('hospital_type'),
                established_year=data.get('established_year'),
                phone=data.get('phone'),
                email=email,
                city=data.get('city'),
                district=data.get('district'),
                website=data.get('website'),
                address=data.get('address'),
                
                total_beds=data.get('total_beds'),
                total_doctors=data.get('total_doctors'),
                description=data.get('description'),
                
                services=[services_str], # Note: ArrayField expects a list, or check your specific setup
                departments=dept_list,   # Passing the list we split above
                
                image=files.get('image'),
                
                emergency_available=emergency_status,
                opd_start=data.get('opd_start'),
                opd_end=data.get('opd_end'),
                achievements=data.get('achievements')
            )

            hospital.save()
            
            messages.success(request, "Registration Submitted Successfully!")
            return redirect('hospital_success')

        except Exception as e:
            print("Error Saving Hospital:", e)
            messages.error(request, f"Something went wrong: {e}")
            return render(request, 'find_hospital/hospital_registration.html')

class Hospital_successView(View):
    def get(self,request):
        return render(request, 'find_hospital/registration_success.html')