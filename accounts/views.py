from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from .forms import CustomUserCreationForm # Make sure this form uses your new User model
from .models import User, PatientProfile

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        # 1. Create the user instance but DO NOT save to DB yet
        user = form.save(commit=False)
        
        # 2. THE FIX: Set username to be the same as email
        # This satisfies the database requirement for a unique username
        user.username = user.email 
        
        # 3. Set default role
        user.role = User.Role.PATIENT
        
        # 4. Now save the user to the database
        user.save()
        
        # 5. Extract mobile number from the validated form data
        mobile = form.cleaned_data.get('mobile_number')
        
        # 6. Create Patient Profile with the mobile number
        PatientProfile.objects.create(user=user, mobile_number=mobile)
        
        messages.success(self.request, 'Registration successful! Please log in.')
        return redirect(self.success_url)

class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        # This method is called when username/password are correct
        user = form.get_user()
        login(self.request, user)
        
        # --- ROLE BASED REDIRECTION ---
        
        # 1. SUPER ADMIN
        if user.is_superuser or user.role == User.Role.ADMIN:
            return redirect('super_admin_overview')
            
        # 2. DOCTOR
        elif user.role == User.Role.DOCTOR:
            # Check if the admin has approved them
            if hasattr(user, 'doctor_profile') and user.doctor_profile.is_approved:
                return redirect('doctor_admin_dashboard')
            else:
                messages.warning(self.request, 'Your account is pending approval by the administrator.')
                return redirect('login') 
            
        # 3. HOSPITAL ADMIN (New)
        elif user.role == User.Role.HOSPITAL_ADMIN:
            return redirect('hospital_admin_overview')
        
        # 3. PATIENT
        elif user.role == User.Role.PATIENT:
            return redirect('home') 
        
        return redirect('home')


class CustomLogoutView(LogoutView):
    next_page = 'login' 
    
    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            messages.success(request, 'You have been logged out successfully.')

        return super().dispatch(request, *args, **kwargs)
    

