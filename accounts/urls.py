from django.urls import path, include
from .views import CustomLoginView
from .views import RegisterView
from .views import CustomLogoutView


urlpatterns = [
    # Your custom login view (this will override the default)
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
    
    path('register/', RegisterView.as_view(), name='register'),
    
    path('', include('allauth.urls')),
    
    path('accounts/', include('django.contrib.auth.urls')), #password_reset
]