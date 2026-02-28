"""
Email Notification Utilities for DocPlus Appointments

Sends real emails via Gmail SMTP (configured in settings.py).
Terminal output is kept for local debugging alongside the real send.
"""

from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings


def _print_email_to_terminal(subject, to_email, body, appointment=None):
    """
    Debug helper — prints the email to terminal so you can see it locally.
    This runs alongside the real send_mail() call.
    """
    print("\n" + "=" * 80)
    print("📧 EMAIL NOTIFICATION (also sending via SMTP)")
    print("=" * 80)
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print("-" * 80)
    print(body)
    print("=" * 80)

    if appointment:
        print(f"[DEBUG] Appointment ID: {appointment.id}")
        print(f"[DEBUG] Call Link Sent: {appointment.call_link_sent}")
        print(f"[DEBUG] Doctor Approved: {appointment.doctor_approved_call}")
        print("=" * 80)
    print("\n")


# ─────────────────────────────────────────────────────────────────────────────
#  1. Appointment Confirmation
# ─────────────────────────────────────────────────────────────────────────────

def send_appointment_confirmation_email(appointment):
    """
    Send appointment confirmation email to patient after booking.

    Args:
        appointment: Appointment model instance
    """
    subject = (
        f"Appointment Confirmed with Dr. "
        f"{appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    )

    body = f"""Dear {appointment.full_name},

Thank you for booking an appointment through DocPlus!

Your appointment has been confirmed with the following details:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APPOINTMENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Doctor: Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}
Specialization: {appointment.doctor.specialization}

Date: {appointment.date.strftime('%B %d, %Y')}
Time: {appointment.start_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}

Consultation Type: {'Video Consultation' if appointment.is_video_consultation else 'In-Person Visit'}
Location: {appointment.doctor.hospital_affiliation.name if appointment.doctor.hospital_affiliation else 'Not specified'}

Reason for Visit: {appointment.reason}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{'📱 Video Call Link will be sent by your doctor closer to the appointment time.' if appointment.is_video_consultation else '📍 Please arrive 10 minutes early for your appointment.'}

For any changes or cancellations, please contact us at {settings.EMAIL_HOST_USER}

Best regards,
The DocPlus Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated message. Please do not reply to this email.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    _print_email_to_terminal(subject, appointment.email, body, appointment)

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.email],
        fail_silently=False,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  2. Video Call Link
# ─────────────────────────────────────────────────────────────────────────────

def send_video_call_link_email(appointment):
    """
    Send video call link email to patient (triggered by doctor from DoctorAdmin).

    Args:
        appointment: Appointment model instance
    """
    subject = (
        f"🎥 Video Call Link - Appointment with Dr. "
        f"{appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    )

    video_call_url = f"https://docplus.com/appointments/video-call/{appointment.video_call_link}/"

    body = f"""Dear {appointment.full_name},

Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name} has shared your video call link!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📹 VIDEO CONSULTATION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Appointment Date: {appointment.date.strftime('%B %d, %Y')}
Appointment Time: {appointment.start_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}

🔗 JOIN VIDEO CALL:
{video_call_url}

🔐 ACCESS CODE: {appointment.call_access_code}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ IMPORTANT INSTRUCTIONS:
• Please join 5 minutes before your scheduled time
• Ensure you have a stable internet connection
• Test your camera and microphone before joining
• Keep your access code ready

For technical support, contact: {settings.EMAIL_HOST_USER}

Best regards,
The DocPlus Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated message. Please do not reply to this email.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    _print_email_to_terminal(subject, appointment.email, body, appointment)

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.email],
        fail_silently=False,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  3. Appointment Reminder (call via cron / Celery task, 24 hrs before)
# ─────────────────────────────────────────────────────────────────────────────

def send_appointment_reminder_email(appointment):
    """
    Send appointment reminder email to patient (24 hours before).
    Typically called by a scheduled task / cron job.

    Args:
        appointment: Appointment model instance
    """
    subject = (
        f"⏰ Reminder: Appointment Tomorrow with Dr. "
        f"{appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    )

    video_call_url = f"https://docplus.com/appointments/video-call/{appointment.video_call_link}/"

    body = f"""Dear {appointment.full_name},

This is a friendly reminder about your upcoming appointment!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 APPOINTMENT REMINDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Doctor: Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}
Date: {appointment.date.strftime('%B %d, %Y')} (Tomorrow)
Time: {appointment.start_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}

Consultation Type: {'Video Consultation' if appointment.is_video_consultation else 'In-Person Visit'}

"""

    if appointment.is_video_consultation and appointment.call_link_sent:
        body += f"""
🔗 VIDEO CALL LINK:
{video_call_url}

🔐 ACCESS CODE: {appointment.call_access_code}

⚡ Quick Tips:
• Join 5 minutes early
• Check your internet connection
• Test camera and microphone
"""
    else:
        body += f"""
📍 LOCATION:
{appointment.doctor.hospital_affiliation.name if appointment.doctor.hospital_affiliation else 'Please check with the clinic'}
{appointment.doctor.hospital_affiliation.address if appointment.doctor.hospital_affiliation and hasattr(appointment.doctor.hospital_affiliation, 'address') else ''}

⚡ Please arrive 10 minutes early
"""

    body += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Need to reschedule? Contact us at: {settings.EMAIL_HOST_USER}

We look forward to seeing you!

Best regards,
The DocPlus Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated message. Please do not reply to this email.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    _print_email_to_terminal(subject, appointment.email, body, appointment)

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.email],
        fail_silently=False,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  4. Appointment Cancellation
# ─────────────────────────────────────────────────────────────────────────────

def send_appointment_cancelled_email(appointment, cancelled_by='patient'):
    """
    Send cancellation confirmation email to patient.

    Args:
        appointment: Appointment model instance
        cancelled_by: 'patient' or 'doctor'
    """
    subject = (
        f"Appointment Cancelled - Dr. "
        f"{appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    )

    body = f"""Dear {appointment.full_name},

Your appointment has been cancelled.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CANCELLED APPOINTMENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Doctor: Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}
Original Date: {appointment.date.strftime('%B %d, %Y')}
Original Time: {appointment.start_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}

Cancelled By: {cancelled_by.title()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If you would like to reschedule, please book a new appointment through our platform.

For assistance, contact: {settings.EMAIL_HOST_USER}

Best regards,
The DocPlus Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated message. Please do not reply to this email.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    _print_email_to_terminal(subject, appointment.email, body)

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.email],
        fail_silently=False,
    )
