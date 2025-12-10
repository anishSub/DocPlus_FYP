from django.urls import path, include
from .views import CustomLoginView
from .views import RegisterView
from .views import CustomLogoutView
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Your custom login view (this will override the default)
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
    
    path('register/', RegisterView.as_view(), name='register'),
    # path('accounts/', include('django.contrib.auth.urls')), #password_reset
    
    
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='forget_password/password_reset_form.html',
            email_template_name='forget_password/password_reset_email.html',
            subject_template_name='forget_password/password_reset_subject.txt', # Optional: if you want custom subject
            success_url='/accounts/password-reset/done/' # Point to step 2
        ), 
        name='password_reset'),

    # 2. Password Reset Done (Success message after submitting email)
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
        template_name='forget_password/password_reset_done.html'
        ), 
        name='password_reset_done'),

    # 3. Password Reset Confirm (The link sent to the user's email)
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
        template_name='forget_password/password_reset_confirm.html'
        ), 
        name='password_reset_confirm'),

    # 4. Password Reset Complete (Success message after changing password)
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
        template_name='forget_password/password_reset_complete.html'
        ), 
        name='password_reset_complete'),
]