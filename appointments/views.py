from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Appointment
from find_doctor.models import DoctorProfile
from datetime import datetime, date, timedelta
import requests
import json
import base64
import hashlib
import hmac
import uuid
import logging
from .email_utils import (
    send_appointment_confirmation_email,
    send_appointment_cancelled_email,
)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

def broadcast_appointment_notification(appointment):
    """Broadcast real-time notification to the doctor via WebSockets"""
    channel_layer = get_channel_layer()
    doctor_group = f"doctor_notifications_{appointment.doctor.id}"
    
    async_to_sync(channel_layer.group_send)(
        doctor_group,
        {
            "type": "new_appointment",
            "appointment": {
                "id": appointment.id,
                "full_name": appointment.full_name,
                "date": appointment.date.strftime('%Y-%m-%d'),
                "time_slot": appointment.time_slot_display,
                "reason": appointment.reason,
                "payment_method": appointment.payment_method,
                "is_video": appointment.is_video_consultation,
            }
        }
    )


#esewa
def _generate_esewa_signature(secret_key, message):
    """Generate HMAC-SHA256 signature in Base64 for eSewa."""
    key = secret_key.encode('utf-8')
    msg = message.encode('utf-8')
    digest = hmac.new(key, msg, hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')



#Apointment boking form
class AppointmentView(View):
    def get(self, request):
        doctors = DoctorProfile.objects.filter(is_approved=True).select_related('user')

        pre_doctor_id = request.GET.get('doctor')
        pre_date = request.GET.get('appointment_date')
        pre_time = request.GET.get('time_slot')

        try:
            pre_doctor_id = int(pre_doctor_id) if pre_doctor_id else None
        except ValueError:
            pre_doctor_id = None

        context = {
            'doctors': doctors,
            'pre_doctor_id': pre_doctor_id,
            'pre_date': pre_date,
            'pre_time': pre_time,
        }
        return render(request, 'appointment/appointment.html', context)


# --------------------------------------------------------------------------- #
#  SAVE APPOINTMENT  (handles all payment methods)
# --------------------------------------------------------------------------- #

@require_POST
def save_appointment(request):
    full_name   = request.POST.get('full_name')
    email       = request.POST.get('email')
    phone       = request.POST.get('phone')
    dob         = request.POST.get('dob')
    gender      = request.POST.get('gender')
    city        = request.POST.get('city')
    address     = request.POST.get('address')

    doctor_id   = request.POST.get('doctor')
    doctor_obj  = get_object_or_404(DoctorProfile, id=doctor_id)
    doctor_name = f"Dr. {doctor_obj.user.first_name} {doctor_obj.user.last_name}"

    appointment_date = request.POST.get('appointment_date')
    time_str         = request.POST.get('time_slot')
    payment_method   = request.POST.get('payment_method')

    # --- Parse time ---
    try:
        start_dt = datetime.strptime(time_str, "%I:%M %p")
        end_dt   = start_dt + timedelta(minutes=30)
    except (ValueError, TypeError):
        return redirect('appointment_page')

    reason          = request.POST.get('reason')
    symptoms        = request.POST.get('symptoms')
    medical_reports = request.FILES.get('medical_reports')

    is_khalti = payment_method == 'khalti'
    is_esewa  = payment_method == 'esewa'

    # --- Create appointment ---
    appointment = Appointment.objects.create(
        user             = request.user if request.user.is_authenticated else None,
        full_name        = full_name,
        email            = email,
        phone            = phone,
        dob              = dob,
        gender           = gender,
        city             = city,
        address          = address,
        doctor           = doctor_obj,
        date             = appointment_date,
        start_time       = start_dt.time(),
        end_time         = end_dt.time(),
        reason           = reason,
        symptoms         = symptoms,
        medical_reports  = medical_reports,
        payment_method   = payment_method,
        status           = 'pending_payment' if (is_khalti or is_esewa) else 'scheduled',
        payment_status   = 'pending' if (is_khalti or is_esewa) else 'completed',
        amount           = doctor_obj.consultation_fee,
    )

    # ------------------------------------------------------------------ #
    #  KHALTI FLOW
    # ------------------------------------------------------------------ #
    if is_khalti:
        callback_url    = request.build_absolute_uri('/appointments/khalti/callback/')
        website_url     = request.build_absolute_uri('/')
        amount_in_paisa = int(doctor_obj.consultation_fee * 100)

        payload = {
            "return_url": callback_url,
            "website_url": website_url,
            "amount": amount_in_paisa,
            "purchase_order_id": f"APPT-{appointment.id}",
            "purchase_order_name": f"Consultation with {doctor_name}",
            "customer_info": {
                "name": full_name,
                "email": email,
                "phone": phone,
            },
            "amount_breakdown": [{"label": "Consultation Fee", "amount": amount_in_paisa}],
            "product_details": [{
                "identity": str(appointment.id),
                "name": f"Video Consultation - {doctor_name}",
                "total_price": amount_in_paisa,
                "quantity": 1,
                "unit_price": amount_in_paisa,
            }],
            "merchant_username": "DocPlus",
            "merchant_extra": f"appointment_id:{appointment.id}",
        }

        headers = {
            'Authorization': f'key {settings.KHALTI_SECRET_KEY}',
            'Content-Type': 'application/json',
        }

        try:
            resp = requests.post(
                f"{settings.KHALTI_BASE_URL}/epayment/initiate/",
                headers=headers,
                data=json.dumps(payload),
                timeout=10,
            )
            data = resp.json()

            if resp.status_code == 200 and 'payment_url' in data:
                appointment.khalti_pidx = data['pidx']
                appointment.save()
                return redirect(data['payment_url'])
            else:
                appointment.payment_status = 'failed'
                appointment.status = 'cancelled'
                appointment.save()
                messages.error(request, data.get('detail', 'Khalti payment initiation failed. Please try again.'))
                return redirect('home')

        except requests.exceptions.RequestException:
            appointment.payment_status = 'failed'
            appointment.status = 'cancelled'
            appointment.save()
            messages.error(request, 'Could not connect to Khalti. Please try again.')
            return redirect('home')

    # ------------------------------------------------------------------ #
    #  ESEWA FLOW
    # ------------------------------------------------------------------ #
    if is_esewa:
        transaction_uuid = str(uuid.uuid4())[:13].replace('-', '')
        total_amount     = int(doctor_obj.consultation_fee)   # in NPR (no paisa for eSewa v2)
        product_code     = settings.ESEWA_PRODUCT_CODE        # 'EPAYTEST' in sandbox

        # Store transaction_uuid so we can look up the appointment in callback
        appointment.khalti_pidx = transaction_uuid  # reuse field for transaction UUID
        appointment.save()

        # Signature message: total_amount,transaction_uuid,product_code
        sign_message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
        signature    = _generate_esewa_signature(settings.ESEWA_SECRET_KEY, sign_message)

        success_url = request.build_absolute_uri('/appointments/esewa/callback/')
        failure_url = request.build_absolute_uri('/appointments/esewa/failure/')

        esewa_context = {
            'esewa_url':        settings.ESEWA_PAYMENT_URL,
            'amount':           total_amount,
            'tax_amount':       0,
            'total_amount':     total_amount,
            'transaction_uuid': transaction_uuid,
            'product_code':     product_code,
            'signature':        signature,
            'success_url':      success_url,
            'failure_url':      failure_url,
        }
        return render(request, 'appointment/esewa_redirect.html', esewa_context)

    # ------------------------------------------------------------------ #
    #  OTHER PAYMENT METHODS (cash, etc.)
    # ------------------------------------------------------------------ #
    # Send confirmation email
    try:
        send_appointment_confirmation_email(appointment)
        broadcast_appointment_notification(appointment)
    except Exception as e:
        logger.error(f"Failed to send confirmation/notification for appointment {appointment.id}: {e}")

    messages.success(
        request,
        f"🎉 Appointment confirmed with {doctor_name} on {appointment_date} at {time_str}! "
        f"A confirmation email has been sent to {email}."
    )
    return redirect('home')


# --------------------------------------------------------------------------- #
#  KHALTI CALLBACK
# --------------------------------------------------------------------------- #

def khalti_callback(request):
    """Khalti redirects here after payment."""
    pidx           = request.GET.get('pidx', '')
    status         = request.GET.get('status', '')
    transaction_id = request.GET.get('transaction_id', '')

    if not pidx:
        messages.error(request, 'Invalid payment callback. Please contact support.')
        return redirect('home')

    appointment = get_object_or_404(Appointment, khalti_pidx=pidx)
    doctor_name = f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"

    # User cancelled
    if status == 'User canceled':
        appointment.payment_status = 'failed'
        appointment.status = 'cancelled'
        appointment.save()
        # Notify patient that appointment was not confirmed
        try:
            send_appointment_cancelled_email(appointment, cancelled_by='patient')
        except Exception as e:
            logger.error(f"Failed to send cancellation email for appointment {appointment.id}: {e}")
        messages.error(request, 'Payment was cancelled. Your appointment has not been confirmed.')
        return redirect('home')





    # Verify via Khalti Lookup API
    headers = {
        'Authorization': f'key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        lookup = requests.post(
            f"{settings.KHALTI_BASE_URL}/epayment/lookup/",
            headers=headers,
            data=json.dumps({"pidx": pidx}),
            timeout=10,
        )
        lookup_data = lookup.json()

        if lookup.status_code == 200 and lookup_data.get('status') == 'Completed':
            appointment.payment_status = 'completed'
            appointment.status         = 'scheduled'
            appointment.save()

            # Send confirmation email to patient
            try:
                send_appointment_confirmation_email(appointment)
                broadcast_appointment_notification(appointment)
            except Exception as e:
                logger.error(f"Failed to send Khalti confirmation/notification for appointment {appointment.id}: {e}")

            return render(request, 'appointment/appointment_success.html', {
                'patient_name':     appointment.full_name,
                'doctor_name':      doctor_name,
                'date':             appointment.date,
                'time':             appointment.time_slot_display,
                'fee':              f"NPR {appointment.amount}",
                'email':            appointment.email,
                'payment_method':   'Khalti',
                'payment_verified': True,
                'transaction_id':   transaction_id or lookup_data.get('transaction_id', ''),
            })

        elif lookup_data.get('status') == 'Pending':
            messages.warning(request, 'Your payment is still being processed. We will confirm your appointment shortly.')
            return redirect('home')

        else:
            appointment.payment_status = 'failed'
            appointment.status         = 'cancelled'
            appointment.save()
            messages.error(request, 'Payment verification failed. Please try booking again or contact support.')
            return redirect('home')

    except requests.exceptions.RequestException:
        messages.error(request, 'Could not verify payment. Please contact support.')
        return redirect('home')



#  ESEWA CALLBACK
def esewa_callback(request):
    """eSewa redirects here with Base64-encoded response in ?data= param."""
    encoded_data = request.GET.get('data', '')

    if not encoded_data:
        messages.error(request, 'Invalid eSewa payment response.')
        return redirect('home')

    try:
        decoded     = base64.b64decode(encoded_data).decode('utf-8')
        response    = json.loads(decoded)
    except Exception:
        messages.error(request, 'Could not decode eSewa response. Please contact support.')
        return redirect('home')

    txn_status       = response.get('status', '')
    transaction_uuid = response.get('transaction_uuid', '')
    total_amount     = response.get('total_amount', 0)
    transaction_code = response.get('transaction_code', '')

    # Verify the signature from eSewa
    signed_fields = response.get('signed_field_names', '').split(',')
    sign_message  = ','.join(f"{f}={response.get(f, '')}" for f in signed_fields if f != 'signature')
    expected_sig  = _generate_esewa_signature(settings.ESEWA_SECRET_KEY, sign_message)
    received_sig  = response.get('signature', '')

    if expected_sig != received_sig:
        messages.error(request, 'eSewa payment signature mismatch. Please contact support.')
        return redirect('home')

    # Find appointment by transaction_uuid stored in khalti_pidx field
    try:
        appointment = Appointment.objects.get(khalti_pidx=transaction_uuid)
    except Appointment.DoesNotExist:
        messages.error(request, 'Could not find your appointment. Please contact support.')
        return redirect('home')

    doctor_name = f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"

    if txn_status == 'COMPLETE':
        appointment.payment_status = 'completed'
        appointment.status         = 'scheduled'
        appointment.save()

        # Send confirmation email to patient
        try:
            send_appointment_confirmation_email(appointment)
            broadcast_appointment_notification(appointment)
        except Exception as e:
            logger.error(f"Failed to send eSewa confirmation/notification for appointment {appointment.id}: {e}")

        return render(request, 'appointment/appointment_success.html', {
            'patient_name':     appointment.full_name,
            'doctor_name':      doctor_name,
            'date':             appointment.date,
            'time':             appointment.time_slot_display,
            'fee':              f"NPR {appointment.amount}",
            'email':            appointment.email,
            'payment_method':   'eSewa',
            'payment_verified': True,
            'transaction_id':   transaction_code,
        })
    else:
        appointment.payment_status = 'failed'
        appointment.status         = 'cancelled'
        appointment.save()
        messages.error(request, f'eSewa payment was not successful (status: {txn_status}). Please try again.')
        return redirect('home')


def esewa_failure(request):
    """Called when eSewa payment fails/is cancelled."""
    # Best-effort: try to notify patient if we can find the appointment
    # eSewa sends transaction_uuid in query params on failure
    messages.error(request, 'eSewa payment failed or was cancelled. Your appointment has not been confirmed.')
    return redirect('home')


# --------------------------------------------------------------------------- #
#  VIDEO CALL
# --------------------------------------------------------------------------- #

class VideoCallView(View):
    """View for accessing video call page"""
    def get(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if request.user.is_authenticated:
            is_patient = appointment.user == request.user
            is_doctor  = appointment.doctor.user == request.user

            if not (is_patient or is_doctor):
                return redirect('/')
        else:
            return redirect('login')

        return render(request, 'appointment/video_call.html', {'appointment': appointment})
# --------------------------------------------------------------------------- #
#  RESCHEDULE & REFUND
# --------------------------------------------------------------------------- #

def can_manage_appointment(appointment):
    """
    Check if the appointment can be rescheduled or refunded.
    Policy: Only if >= 24 hours before the appointment.
    """
    now = datetime.now()
    appt_dt = datetime.combine(appointment.date, appointment.start_time)
    diff = appt_dt - now
    return diff.total_seconds() >= 86400  # 24 hours


@login_required
def manage_appointment(request, appointment_id):
    """Page for patient to reschedule or cancel/refund their appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    can_manage = can_manage_appointment(appointment)
    
    # Get available slots for the doctor (for reschedule)
    doctors = DoctorProfile.objects.filter(is_approved=True).select_related('user')
    
    context = {
        'appointment': appointment,
        'can_manage': can_manage,
        'doctors': doctors, # For selecting new times
        'today': date.today(),
    }
    return render(request, 'appointment/manage_appointment.html', context)


@require_POST
@login_required
def reschedule_appointment(request, appointment_id):
    """Process reschedule request"""
    old_appt = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    if not can_manage_appointment(old_appt):
        messages.error(request, "Appointments can only be rescheduled up to 24 hours in advance.")
        return redirect('manage_appointment', appointment_id=appointment_id)

    new_date_str = request.POST.get('appointment_date')
    new_time_str = request.POST.get('time_slot')

    try:
        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
        start_dt = datetime.strptime(new_time_str, "%I:%M %p")
        end_dt = start_dt + timedelta(minutes=30)
    except (ValueError, TypeError):
        messages.error(request, "Invalid date or time slot selected.")
        return redirect('manage_appointment', appointment_id=appointment_id)

    # Create new appointment cloned from old one
    new_appt = Appointment.objects.create(
        user=old_appt.user,
        full_name=old_appt.full_name,
        email=old_appt.email,
        phone=old_appt.phone,
        dob=old_appt.dob,
        gender=old_appt.gender,
        city=old_appt.city,
        address=old_appt.address,
        doctor=old_appt.doctor,
        date=new_date,
        start_time=start_dt.time(),
        end_time=end_dt.time(),
        reason=old_appt.reason,
        symptoms=old_appt.symptoms,
        medical_reports=old_appt.medical_reports,
        payment_method=old_appt.payment_method,
        amount=old_appt.amount,
        status='scheduled',
        payment_status=old_appt.payment_status,
        rescheduled_from=old_appt,
        is_video_consultation=old_appt.is_video_consultation
    )

    # Cancel old appointment
    old_appt.status = 'cancelled'
    old_appt.save()

    # Send notifications
    try:
        from .email_utils import send_reschedule_notification_email
        send_reschedule_notification_email(new_appt, old_appt)
        broadcast_appointment_notification(new_appt)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Reschedule notification failed: {e}")

    messages.success(request, f"Appointment successfully rescheduled to {new_date} at {new_time_str}!")
    return redirect('home')


@require_POST
@login_required
def cancel_and_refund(request, appointment_id):
    """Process cancellation and refund request"""
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    reason = request.POST.get('cancellation_reason', 'Patient requested cancellation.')

    if not can_manage_appointment(appointment):
        messages.error(request, "Appointments can only be cancelled/refunded up to 24 hours in advance.")
        return redirect('manage_appointment', appointment_id=appointment_id)

    appointment.status = 'cancelled'
    appointment.cancellation_reason = reason
    appointment.refund_status = 'requested'
    appointment.refund_requested_at = datetime.now()
    
    # --- KHALTI AUTOMATIC REFUND (DEMO) ---
    if appointment.payment_method == 'khalti' and appointment.payment_status == 'completed' and appointment.khalti_pidx:
        import requests
        headers = {
            'Authorization': f'key {settings.KHALTI_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        payload = {
            "pidx": appointment.khalti_pidx,
            "amount": int(appointment.amount * 100), # in paisa
            "reason": reason
        }
        
        try:
            resp = requests.post(
                f"{settings.KHALTI_BASE_URL}/epayment/refund/",
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            if resp.status_code == 200:
                appointment.refund_status = 'completed'
                messages.success(request, "Appointment cancelled and Khalti refund processed successfully!")
            else:
                messages.warning(request, "Appointment cancelled. Khalti refund is being processed manually.")
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Khalti refund API call failed: {e}")
            messages.warning(request, "Appointment cancelled. Refund request submitted.")
    
    # --- ESEWA (MANUAL STATUS) ---
    elif appointment.payment_method == 'esewa' and appointment.payment_status == 'completed':
        messages.success(request, "Appointment cancelled. Your eSewa refund request has been submitted for manual processing.")
    
    else:
        messages.success(request, "Appointment cancelled successfully.")

    appointment.save()
    
    # Notify via email
    try:
        from .email_utils import send_appointment_cancelled_email
        send_appointment_cancelled_email(appointment, cancelled_by='patient')
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Cancellation email failed: {e}")

    return redirect('home')
