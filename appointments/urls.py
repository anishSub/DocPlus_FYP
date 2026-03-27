
from django.urls import path
from .views import (
    AppointmentView,
    save_appointment,
    khalti_callback,
    esewa_callback,
    esewa_failure,
    VideoCallView,
    manage_appointment,
    reschedule_appointment,
    cancel_and_refund,
)

urlpatterns = [
    path('appointment/', AppointmentView.as_view(), name='appointment_page'),
    path('save-appointment/', save_appointment, name='save_appointment'),

    # Khalti
    path('khalti/callback/', khalti_callback, name='khalti_callback'),

    # eSewa
    path('esewa/callback/', esewa_callback, name='esewa_callback'),
    path('esewa/failure/', esewa_failure, name='esewa_failure'),

    # Video Call
    path('video-call/<int:appointment_id>/', VideoCallView.as_view(), name='video_call'),

    # Reschedule & Refund
    path('manage/<int:appointment_id>/', manage_appointment, name='manage_appointment'),
    path('reschedule/<int:appointment_id>/', reschedule_appointment, name='reschedule_appointment'),
    path('cancel-refund/<int:appointment_id>/', cancel_and_refund, name='cancel_and_refund'),
]
