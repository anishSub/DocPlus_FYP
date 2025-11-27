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
        # The form's clean_email() method already validates uniqueness
        # The form's save() method handles:
        # - Saves first_name, last_name, email to User
        # - Creates UserProfile with mobile_number
        response = super().form_valid(form)
        
        # Add success message
        messages.success(self.request, 'Registration successful! Please log in.')
        
        return response
    
    def form_invalid(self, form):
        # This runs when validation fails (duplicate email, etc.)
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)



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
            # Use filter instead of get to handle duplicates
            users = User.objects.filter(email=email)
            
            if not users.exists():
                messages.error(request, 'Invalid email or password')
                return render(request, self.template_name)
            
            # If multiple users with same email, try to authenticate each one
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
                
                return redirect(self.get_success_url())
            else:
                messages.error(request, 'Invalid email or password')
                return render(request, self.template_name)
                
        except Exception as e:
            messages.error(request, 'An error occurred during login. Please try again.')
            return render(request, self.template_name)




class CustomLogoutView(LogoutView):
    next_page = 'home'
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)