from django.shortcuts import render
from django.views import View

# Create your views here.
class FindHospitalView(View):
    def get(self, request):
        return render(request, 'find_hospital/find_hospital.html')
    
class HospitalDetailView(View):
    def get(self, request):
        return render(request, 'find_hospital/hospital_detail.html')