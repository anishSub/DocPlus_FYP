from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.views.decorators.http import require_POST



class AppointmentPersonalInfoView(View):
    # Handle viewing the page
    def get(self, request):
        return render(request, 'appointment/appointment_personal_info.html')

    # Handle the form submission
    def post(self, request):
        request.session['appointment_data'] = request.POST
        return redirect('appointment_info')

class AppointmentInfoView(View):
    def get(self, request):
        # This points to your new template file
        return render(request, 'appointment/appointment_appointment_info.html')
    
    def post(self, request):
        request.session['appointment_data1'] = request.POST
        return redirect('appointment_medical_info')
    
class AppointmentMedicalInfoView(View):
    def get(self, request):
        # This points to your new template file
        return render(request, 'appointment/appointment_medical_info.html')
    
    def post(self, request):
        # Process final appointment data here
        request.session['appointment_data2'] = request.POST
        return redirect('appointment_payment')

class AppointmentPaymentView(View):
    def get(self, request):
        return render(request, 'appointment/appointment_payment.html')
    
    def post(self, request):
        # Process final appointment data here
        request.session['appointment_data3'] = request.POST
        return redirect('appointment_success')
    
class AppointmentSuccessView(View):
    def get(self, request):
        return render(request, 'appointment/appointment_success.html')
