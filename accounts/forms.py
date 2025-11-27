from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'})
    )
    mobile_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Mobile Number'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'mobile_number', 'password1', 'password2')
    
    def clean_email(self):
        """
        Validate that the email is unique
        """
        email = self.cleaned_data.get('email')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'This email address is already registered. '
                'Please use a different email or try logging in.'
            )
        
        return email
    
    def clean_username(self):
        """
        Validate that the username is unique (Django handles this by default, but being explicit)
        """
        username = self.cleaned_data.get('username')
        
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                'This username is already taken. Please choose a different username.'
            )
        
        return username
    
    def save(self, commit=True):
        # Save the User instance
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create UserProfile with mobile number
            UserProfile.objects.create(
                user=user,
                mobile_number=self.cleaned_data['mobile_number']
            )
        
        return user