"""
Email Notification Utilities for DocPlus Appointments

Sends real emails via Gmail SMTP (configured in settings.py).
All emails use HTML for a premium, professional appearance.
"""

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# DocPlus logo — publicly accessible URL for email clients
LOGO_URL = "https://i.imgur.com/EyG3CHE.png"

# DocPlus primary gradient colours
PRIMARY_COLOR = "#1447E6"
SECONDARY_COLOR = "#0092B8"
DARK_COLOR = "#1C398E"


def _base_html(title: str, body_html: str) -> str:
    """
    Wrap any email content in a consistent, professional DocPlus HTML shell.
    Compatible with all major email clients (table-based layout).
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background-color:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f0f4f8;padding:40px 0;">
    <tr>
      <td align="center">

        <!-- Card -->
        <table width="600" cellpadding="0" cellspacing="0" border="0"
               style="background:#ffffff;border-radius:16px;overflow:hidden;
                      box-shadow:0 4px 24px rgba(0,0,0,0.08);max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(90deg,{SECONDARY_COLOR} 0%,{PRIMARY_COLOR} 50%,{DARK_COLOR} 100%);
                       padding:32px 40px;text-align:center;">
              <img src="{LOGO_URL}" alt="DocPlus Logo" style="height:40px; width:auto; display:block; margin: 0 auto; border:0;">
              <p style="color:rgba(255,255,255,0.85);margin:6px 0 0;font-size:14px;letter-spacing:1px;">
                HEALTHCARE AT YOUR FINGERTIPS
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              {body_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8fafc;padding:24px 40px;border-top:1px solid #e2e8f0;text-align:center;">
              <p style="color:#94a3b8;font-size:13px;margin:0 0 4px;">
                This is an automated message — please do not reply to this email.
              </p>
              <p style="color:#94a3b8;font-size:13px;margin:0;">
                Need help? Contact us at
                <a href="mailto:{settings.EMAIL_HOST_USER}"
                   style="color:{PRIMARY_COLOR};text-decoration:none;">{settings.EMAIL_HOST_USER}</a>
              </p>
              <p style="color:#cbd5e1;font-size:12px;margin:12px 0 0;">
                &copy; 2025 DocPlus. All rights reserved.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>"""


def _info_row(label: str, value: str) -> str:
    """A single label/value row inside an info table."""
    return f"""
    <tr>
      <td style="padding:10px 16px;color:#64748b;font-size:14px;font-weight:600;
                 width:40%;border-bottom:1px solid #f1f5f9;">{label}</td>
      <td style="padding:10px 16px;color:#1e293b;font-size:14px;font-weight:500;
                 border-bottom:1px solid #f1f5f9;">{value}</td>
    </tr>"""


def _info_table(rows_html: str) -> str:
    """Wraps rows in a styled info table."""
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;
                  margin-top:24px;margin-bottom:24px;">
      {rows_html}
    </table>"""


def _section_title(text: str, color: str = PRIMARY_COLOR) -> str:
    return f"""<h2 style="color:{color};font-size:18px;font-weight:700;margin:0 0 4px;">{text}</h2>
               <div style="width:40px;height:3px;background:linear-gradient(90deg,{SECONDARY_COLOR},{PRIMARY_COLOR});
                           border-radius:2px;margin-bottom:20px;"></div>"""


def _send(subject: str, to_email: str, html: str, plain: str = "") -> None:
    """Send an HTML email via SMTP."""
    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain or "Please view this email in an HTML-compatible email client.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html, "text/html")
    msg.send(fail_silently=False)


# ─────────────────────────────────────────────────────────────────────────────
#  1. Appointment Confirmation
# ─────────────────────────────────────────────────────────────────────────────

def send_appointment_confirmation_email(appointment):
    doctor_name = f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    subject = f"Appointment Confirmed — {doctor_name}"

    consult_type = "Video Consultation" if appointment.is_video_consultation else "In-Person Visit"
    hospital = appointment.doctor.hospital_affiliation.name if appointment.doctor.hospital_affiliation else "To be confirmed"

    rows = (
        _info_row("Doctor", doctor_name) +
        _info_row("Specialization", appointment.doctor.specialization) +
        _info_row("Date", appointment.date.strftime("%B %d, %Y")) +
        _info_row("Time", f"{appointment.start_time.strftime('%I:%M %p')} &ndash; {appointment.end_time.strftime('%I:%M %p')}") +
        _info_row("Consultation Type", consult_type) +
        _info_row("Location", hospital) +
        _info_row("Reason", appointment.reason)
    )

    note = (
        "Your doctor will send you the video call link closer to the appointment time."
        if appointment.is_video_consultation else
        "Please arrive 10 minutes early for your appointment."
    )

    body_html = f"""
    <p style="color:#1e293b;font-size:22px;font-weight:700;margin:0 0 8px;">
      Hi {appointment.full_name},
    </p>
    <p style="color:#64748b;font-size:15px;line-height:1.7;margin:0 0 20px;">
      Your appointment has been <strong style="color:#22c55e;">confirmed</strong>.
      Here is a summary of your booking:
    </p>

    {_section_title("Appointment Details")}
    {_info_table(rows)}

    <div style="background:#eff6ff;border-left:4px solid {PRIMARY_COLOR};border-radius:8px;
                padding:16px 20px;margin-top:8px;">
      <p style="margin:0;color:{PRIMARY_COLOR};font-size:14px;font-weight:600;">{note}</p>
    </div>
    """

    _send(subject, appointment.email, _base_html(subject, body_html))


# ─────────────────────────────────────────────────────────────────────────────
#  2. Video Call Link
# ─────────────────────────────────────────────────────────────────────────────

def send_video_call_link_email(appointment, request=None):
    doctor_name = f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    subject = f"Join Your Video Consultation — {doctor_name}"

    if request:
        video_call_url = request.build_absolute_uri(f"/appointments/video-call/{appointment.id}/")
    else:
        video_call_url = f"http://127.0.0.1:8000/appointments/video-call/{appointment.id}/"

    rows = (
        _info_row("Doctor", doctor_name) +
        _info_row("Date", appointment.date.strftime("%B %d, %Y")) +
        _info_row("Time", f"{appointment.start_time.strftime('%I:%M %p')} &ndash; {appointment.end_time.strftime('%I:%M %p')}") +
        _info_row("Access Code", f"<strong style='font-size:18px;letter-spacing:4px;color:{PRIMARY_COLOR};'>{appointment.call_access_code}</strong>")
    )

    body_html = f"""
    <p style="color:#1e293b;font-size:22px;font-weight:700;margin:0 0 8px;">
      Hi {appointment.full_name},
    </p>
    <p style="color:#64748b;font-size:15px;line-height:1.7;margin:0 0 20px;">
      {doctor_name} is ready for your video consultation. Click the button below to join now.
    </p>

    {_section_title("Consultation Details")}
    {_info_table(rows)}

    <div style="text-align:center;margin:32px 0;">
      <a href="{video_call_url}"
         style="background:linear-gradient(90deg,{SECONDARY_COLOR},{PRIMARY_COLOR});
                color:#ffffff;text-decoration:none;padding:16px 40px;
                border-radius:50px;font-size:16px;font-weight:700;
                display:inline-block;box-shadow:0 4px 16px rgba(20,71,230,0.3);">
        Join Video Call &rarr;
      </a>
    </div>

    <p style="color:#94a3b8;font-size:13px;text-align:center;">
      Or copy this link: <a href="{video_call_url}" style="color:{PRIMARY_COLOR};">{video_call_url}</a>
    </p>

    <div style="background:#f0fdf4;border-left:4px solid #22c55e;border-radius:8px;
                padding:16px 20px;margin-top:16px;">
      <p style="margin:0;color:#166534;font-size:14px;font-weight:600;">
        Tips: Join 5 minutes early &bull; Ensure stable internet &bull; Allow camera &amp; microphone access
      </p>
    </div>
    """

    _send(subject, appointment.email, _base_html(subject, body_html))


# ─────────────────────────────────────────────────────────────────────────────
#  3. Appointment Reminder
# ─────────────────────────────────────────────────────────────────────────────

def send_appointment_reminder_email(appointment):
    doctor_name = f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    subject = f"Reminder: Your Appointment is Tomorrow — {doctor_name}"

    consult_type = "Video Consultation" if appointment.is_video_consultation else "In-Person Visit"
    rows = (
        _info_row("Doctor", doctor_name) +
        _info_row("Date", f"{appointment.date.strftime('%B %d, %Y')} (Tomorrow)") +
        _info_row("Time", f"{appointment.start_time.strftime('%I:%M %p')} &ndash; {appointment.end_time.strftime('%I:%M %p')}") +
        _info_row("Consultation Type", consult_type)
    )

    extra = ""
    if appointment.is_video_consultation and appointment.call_link_sent:
        video_url = f"http://127.0.0.1:8000/appointments/video-call/{appointment.id}/"
        extra = f"""
        <div style="text-align:center;margin:24px 0;">
          <a href="{video_url}"
             style="background:linear-gradient(90deg,{SECONDARY_COLOR},{PRIMARY_COLOR});
                    color:#fff;text-decoration:none;padding:14px 36px;
                    border-radius:50px;font-size:15px;font-weight:700;display:inline-block;">
            Join Video Call &rarr;
          </a>
        </div>"""
    else:
        hospital = appointment.doctor.hospital_affiliation.name if appointment.doctor.hospital_affiliation else "Please confirm with the clinic"
        extra = f"""
        <div style="background:#f8fafc;border-radius:8px;padding:16px 20px;margin-top:16px;">
          <p style="margin:0;color:#475569;font-size:14px;">
            <strong>Location:</strong> {hospital}
          </p>
          <p style="margin:8px 0 0;color:#475569;font-size:14px;">Please arrive 10 minutes early.</p>
        </div>"""

    body_html = f"""
    <p style="color:#1e293b;font-size:22px;font-weight:700;margin:0 0 8px;">
      Hi {appointment.full_name},
    </p>
    <p style="color:#64748b;font-size:15px;line-height:1.7;margin:0 0 20px;">
      This is a friendly reminder about your upcoming appointment tomorrow.
    </p>

    {_section_title("Appointment Reminder")}
    {_info_table(rows)}
    {extra}
    """

    _send(subject, appointment.email, _base_html(subject, body_html))


# ─────────────────────────────────────────────────────────────────────────────
#  4. Appointment Cancellation
# ─────────────────────────────────────────────────────────────────────────────

def send_appointment_cancelled_email(appointment, cancelled_by='patient'):
    doctor_name = f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
    subject = f"Appointment Cancelled — {doctor_name}"

    rows = (
        _info_row("Doctor", doctor_name) +
        _info_row("Original Date", appointment.date.strftime("%B %d, %Y")) +
        _info_row("Original Time", f"{appointment.start_time.strftime('%I:%M %p')} &ndash; {appointment.end_time.strftime('%I:%M %p')}") +
        _info_row("Cancelled By", cancelled_by.title())
    )

    body_html = f"""
    <p style="color:#1e293b;font-size:22px;font-weight:700;margin:0 0 8px;">
      Hi {appointment.full_name},
    </p>
    <p style="color:#64748b;font-size:15px;line-height:1.7;margin:0 0 20px;">
      Your appointment has been <strong style="color:#ef4444;">cancelled</strong>.
      Here are the details of the cancelled booking:
    </p>

    {_section_title("Cancelled Appointment", color="#ef4444")}
    {_info_table(rows)}

    <div style="background:#fff7ed;border-left:4px solid #f97316;border-radius:8px;
                padding:16px 20px;margin-top:8px;">
      <p style="margin:0;color:#9a3412;font-size:14px;font-weight:600;">
        Would you like to reschedule? You can book a new appointment any time through DocPlus.
      </p>
    </div>
    """

    _send(subject, appointment.email, _base_html(subject, body_html))


# ─────────────────────────────────────────────────────────────────────────────
#  5. Reschedule Notification
# ─────────────────────────────────────────────────────────────────────────────

def send_reschedule_notification_email(new_appointment, old_appointment):
    doctor_name = f"Dr. {new_appointment.doctor.user.get_full_name()}"
    subject = f"Appointment Rescheduled — {doctor_name}"

    new_rows = (
        _info_row("Doctor", doctor_name) +
        _info_row("New Date", new_appointment.date.strftime("%B %d, %Y")) +
        _info_row("New Time", f"{new_appointment.start_time.strftime('%I:%M %p')} &ndash; {new_appointment.end_time.strftime('%I:%M %p')}") +
        _info_row("Consultation Type", "Video Consultation" if new_appointment.is_video_consultation else "In-Person Visit")
    )

    old_rows = (
        _info_row("Previous Date", old_appointment.date.strftime("%B %d, %Y")) +
        _info_row("Previous Time", old_appointment.start_time.strftime("%I:%M %p"))
    )

    body_html = f"""
    <p style="color:#1e293b;font-size:22px;font-weight:700;margin:0 0 8px;">
      Hi {new_appointment.full_name},
    </p>
    <p style="color:#64748b;font-size:15px;line-height:1.7;margin:0 0 20px;">
      Your appointment has been successfully <strong style="color:{PRIMARY_COLOR};">rescheduled</strong>.
    </p>

    {_section_title("New Appointment")}
    {_info_table(new_rows)}

    {_section_title("Previous Appointment (Cancelled)", color="#94a3b8")}
    {_info_table(old_rows)}

    <div style="background:#eff6ff;border-left:4px solid {PRIMARY_COLOR};border-radius:8px;
                padding:16px 20px;margin-top:8px;">
      <p style="margin:0;color:{PRIMARY_COLOR};font-size:14px;font-weight:600;">
        You can manage your appointment through your DocPlus dashboard.
      </p>
    </div>
    """

    _send(subject, new_appointment.email, _base_html(subject, body_html))
