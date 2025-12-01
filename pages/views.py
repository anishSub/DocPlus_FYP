from django.shortcuts import render
from django.views import View


# Create your views here.
class HomeView(View):
    def get(self, request):
        return render(request, 'home/home.html')
    
class AboutUsView(View):
    def get(self, request):
        return render(request, 'about_us/about_us.html')
    
class ContactUsView(View):
    def get(self, request):
        return render(request, 'contact_us/contact_us.html')
