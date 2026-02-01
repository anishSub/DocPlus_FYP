
from django.urls import path
from .views import AppointmentView, save_appointment, VideoCallView



urlpatterns = [
    path('appointment/', AppointmentView.as_view(), name='appointment_page'),
    path('save-appointment/', save_appointment, name='save_appointment'),
    path('video-call/<int:appointment_id>/', VideoCallView.as_view(), name='video_call'),
]
