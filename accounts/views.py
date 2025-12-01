from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib.auth.models import User



class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        # 1. Prepare the user object but don't save to database yet
        user = form.save(commit=False)
        
        # 2. EXPLICITLY set user type to Patient
        # (Since we removed the radio buttons from HTML, we enforce it here)
        user.is_patient = True  
        user.is_doctor = False
        user.is_staff = False   # Security measure: ensure they are not admin
        user.is_superuser = False
        
        # 3. Now save to the database
        user.save()
        
        # 4. If your CustomUserCreationForm has "save_m2m" logic or profile creation, 
        # you might need to call it here manually if it was skipped by commit=False.
        # Usually, standard UserCreationForms are fine with just user.save()
        
        messages.success(self.request, 'Registration successful! Please log in.')
        
        # Redirect to the success URL (Login page)
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

# ... (Your Login and Logout views remain exactly the same, they are fine)

# login
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('home')
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Try to find user by email - handle multiple or no users
        try:
            # Use filter instead of get to handle potential duplicates safely
            users = User.objects.filter(email=email)
            
            if not users.exists():
                messages.error(request, 'Invalid email or password')
                return render(request, self.template_name)
            
            # If multiple users with same email exist (which shouldn't happen with new form logic), 
            # try to authenticate each one
            authenticated_user = None
            
            for user_obj in users:
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    authenticated_user = user
                    break
            
            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(request, f'Welcome back, {authenticated_user.first_name or authenticated_user.username}!')
                
                # Handle remember me
                if not request.POST.get('remember'):
                    request.session.set_expiry(0)
                
                # --- HIERARCHY REDIRECTION LOGIC ---
                
                # PRIORITY 1: ADMIN / STAFF
                if authenticated_user.is_superuser or authenticated_user.is_staff:
                    return redirect('/admin/')
                
                # PRIORITY 2: DOCTOR
                # Check safely if the user has the is_doctor attribute
                elif getattr(authenticated_user, 'is_doctor', False):
                    # IMPORTANT: You must create a URL named 'doctor_dashboard' later.
                    # For now, if it doesn't exist, it will crash unless you change this line.
                    # Example: return redirect('home') until dashboard is ready.
                    return redirect('doctor_dashboard') 
                
                # PRIORITY 3: PATIENT (Default)
                else:
                    return redirect('home')
                
                # -----------------------------------

            else:
                messages.error(request, 'Invalid email or password')
                return render(request, self.template_name)
                
        except Exception as e:
            # It's good practice to log the error 'e' for debugging, even if not showing it to user
            print(f"Login Error: {e}") 
            messages.error(request, 'An error occurred during login. Please try again.')
            return render(request, self.template_name)




class CustomLogoutView(LogoutView):
    next_page = 'home'
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)
    

