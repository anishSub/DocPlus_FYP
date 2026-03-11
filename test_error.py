import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from appointments.models import Appointment
from doctorAdmin.views import send_video_call_link
from django.test import RequestFactory

try:
    print("Testing send_video_call_link...")
    app = Appointment.objects.first()
    if not app:
        print("No appointments found!")
        exit()
        
    user = app.doctor.user
    request = RequestFactory().post(f'/doctor/send-video-link/{app.id}/')
    request.user = user
    
    response = send_video_call_link(request, app.id)
    print("Response status:", response.status_code)
    print("Response content:", response.content)
except Exception as e:
    import traceback
    traceback.print_exc()
