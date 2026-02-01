"""
Email Notification Utilities for DocPlus Appointments

This module provides email notification functions that currently print to terminal.
Once SMTP is configured, these functions can be easily updated to send actual emails.
"""

from datetime import datetime


def _print_email_to_terminal(subject, to_email, body, appointment=None):
    """
    Helper function to print email content to terminal in a formatted way.
    This simulates sending an email for testing purposes.
    
    Args:
        subject (str): Email subject line
        to_email (str): Recipient email address
        body (str): Email body content
        appointment (Appointment, optional): Related appointment object for additional context
    """
    print("\n" + "=" * 80)
    print("📧 EMAIL NOTIFICATION")
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


def send_appointment_confirmation_email(appointment):
    """
    Send appointment confirmation email to patient after booking.
    
    Args:
        appointment: Appointment model instance
    """
    subject = f"Appointment Confirmed with Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    
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

For any changes or cancellations, please contact us at support@docplus.com

Best regards,
The DocPlus Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated message. Please do not reply to this email.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    _print_email_to_terminal(subject, appointment.email, body, appointment)
    
    # TODO: Uncomment when SMTP is configured
    # from django.core.mail import send_mail
    # send_mail(
    #     subject,
    #     body,
    #     'noreply@docplus.com',
    #     [appointment.email],
    #     fail_silently=False,
    # )


def send_video_call_link_email(appointment):
    """
    Send video call link email to patient (triggered by doctor).
    
    Args:
        appointment: Appointment model instance
    """
    subject = f"🎥 Video Call Link - Appointment with Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    
    # Generate the video call URL (adjust based on your actual video call route)
    video_call_url = f"http://localhost:8000/appointments/video-call/{appointment.video_call_link}/"
    
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

For technical support, contact: support@docplus.com

Best regards,
The DocPlus Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated message. Please do not reply to this email.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    _print_email_to_terminal(subject, appointment.email, body, appointment)
    
    # TODO: Uncomment when SMTP is configured
    # from django.core.mail import send_mail
    # send_mail(
    #     subject,
    #     body,
    #     'noreply@docplus.com',
    #     [appointment.email],
    #     fail_silently=False,
    # )


def send_appointment_reminder_email(appointment):
    """
    Send appointment reminder email to patient (24 hours before).
    This would typically be called by a scheduled task/cron job.
    
    Args:
        appointment: Appointment model instance
    """
    subject = f"⏰ Reminder: Appointment Tomorrow with Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    
    video_call_url = f"http://localhost:8000/appointments/video-call/{appointment.video_call_link}/"
    
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

Need to reschedule? Contact us at: support@docplus.com

We look forward to seeing you!

Best regards,
The DocPlus Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated message. Please do not reply to this email.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    _print_email_to_terminal(subject, appointment.email, body, appointment)
    
    # TODO: Uncomment when SMTP is configured
    # from django.core.mail import send_mail
    # send_mail(
    #     subject,
    #     body,
    #     'noreply@docplus.com',
    #     [appointment.email],
    #     fail_silently=False,
    # )


def send_appointment_cancelled_email(appointment, cancelled_by='patient'):
    """
    Send cancellation confirmation email.
    
    Args:
        appointment: Appointment model instance
        cancelled_by: 'patient' or 'doctor'
    """
    subject = f"Appointment Cancelled - Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    
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

For assistance, contact: support@docplus.com

Best regards,
The DocPlus Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    _print_email_to_terminal(subject, appointment.email, body, appointment)
