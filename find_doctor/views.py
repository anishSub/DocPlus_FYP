from django.shortcuts import render
from django.views import View

# Create your views here.
class FindDoctorView(View):
    def get(self, request):
        return render(request, 'find_doctor/find_doctor.html')
    
    
class DcotorDetailsView(View):
    def get(self, request):
        return render(request, 'find_doctor/doctor_detail.html')

class DoctorRegistrationView(View):
    def get(self, request):
        return render(request, 'find_doctor/doctor_registration.html')
    
