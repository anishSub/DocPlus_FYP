# E-Payment Integration Guide (Khalti & eSewa)

This document explains how the Khalti and eSewa payment gateways are integrated into this Django application.

## 1. Overview
The application handles appointments and gives users the option to pay via Khalti or eSewa. Both integrations use the **server-side API approach** (specifically, eSewa v2 and Khalti ePayment API v2).

- **Khalti flow:** The backend makes an API request to initiate the payment. Khalti returns a `payment_url` and a `pidx` (Payment ID). The user is redirected to the URL. After payment, Khalti redirects them back to our callback URL where we verify the payment using the `pidx`.
- **eSewa flow:** The backend generates an HMAC-SHA256 signature and returns an HTML form with hidden fields. This form automatically submits (POSTs) to eSewa. After payment, eSewa redirects back to our callback URL with base64-encoded transaction details, which we decode and verify using the signature.

---

## 2. Environment Variables & Settings

Both gateways require credentials that are kept secret in the `.env` file and loaded in `settings.py`.

### `.env` File
```env
# Khalti Payment Gateway (Sandbox)
KHALTI_SECRET_KEY='your_live_secret_key'
KHALTI_PUBLIC_KEY='your_live_public_key'

# eSewa Payment Gateway (Sandbox/UAT)
ESEWA_SECRET_KEY='8gBm/:&EnhH.1/q' # Universal test key
ESEWA_PRODUCT_CODE='EPAYTEST'      # Universal test merchant code
ESEWA_PAYMENT_URL='https://rc-epay.esewa.com.np/api/epay/main/v2/form'
```

### `settings.py`
```python
import os

KHALTI_SECRET_KEY = os.getenv('KHALTI_SECRET_KEY')
KHALTI_BASE_URL = 'https://dev.khalti.com/api/v2'

ESEWA_SECRET_KEY    = os.getenv('ESEWA_SECRET_KEY', '8gBm/:&EnhH.1/q')
ESEWA_PRODUCT_CODE  = os.getenv('ESEWA_PRODUCT_CODE', 'EPAYTEST')
ESEWA_PAYMENT_URL   = os.getenv('ESEWA_PAYMENT_URL')
```

---

## 3. Database Modifications (`models.py`)

The `Appointment` model needs fields to store the payment statuses and transaction identifiers.

```python
class Appointment(models.DateField):
    # ... other fields ...
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    khalti_pidx    = models.CharField(max_length=255, blank=True, null=True) # Used for both Khalti pidx and eSewa UUID
```

---

## 4. Initiating Payments (`views.py`)

When the user submits the appointment form (`save_appointment` view), the backend prepares the request for the selected gateway.

### Khalti Initiation
```python
if payment_method == 'khalti':
    payload = {
        "return_url": request.build_absolute_uri('/appointments/khalti/callback/'),
        "website_url": request.build_absolute_uri('/'),
        "amount": int(doctor_fee * 100), # Khalti expects Paisa
        "purchase_order_id": f"APPT-{appointment.id}",
        "purchase_order_name": "Consultation",
        "customer_info": {"name": full_name, "email": email, "phone": phone}
    }
    headers = {
        'Authorization': f'key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    
    # Send request to Khalti
    resp = requests.post(f"{settings.KHALTI_BASE_URL}/epayment/initiate/", headers=headers, json=payload)
    data = resp.json()
    
    # Save the pidx and redirect to payment page
    appointment.khalti_pidx = data['pidx']
    appointment.save()
    return redirect(data['payment_url'])
```

### eSewa Initiation
eSewa v2 requires an HMAC-SHA256 signature generated on the backend.
```python
import base64, hashlib, hmac, uuid

def _generate_esewa_signature(secret_key, message):
    key = secret_key.encode('utf-8')
    msg = message.encode('utf-8')
    digest = hmac.new(key, msg, hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')

if payment_method == 'esewa':
    transaction_uuid = str(uuid.uuid4())[:13].replace('-', '')
    total_amount = int(doctor_fee) # eSewa expects NPR (not Paisa)
    
    appointment.khalti_pidx = transaction_uuid
    appointment.save()
    
    # Generate signature
    sign_message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={settings.ESEWA_PRODUCT_CODE}"
    signature = _generate_esewa_signature(settings.ESEWA_SECRET_KEY, sign_message)
    
    context = {
        'esewa_url': settings.ESEWA_PAYMENT_URL,
        'amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': settings.ESEWA_PRODUCT_CODE,
        'signature': signature,
        # ... success and failure URLs ...
    }
    # Render a template that auto-POSTs this data to eSewa
    return render(request, 'appointment/esewa_redirect.html', context)
```

---

## 5. Handling Callbacks (`views.py`)

After the user pays, the gateways redirect back to our system to verify the transaction.

### Khalti Callback (`khalti_callback`)
```python
def khalti_callback(request):
    pidx = request.GET.get('pidx')
    appointment = get_object_or_404(Appointment, khalti_pidx=pidx)
    
    # Call Khalti Lookup API to verify
    headers = {'Authorization': f'key {settings.KHALTI_SECRET_KEY}'}
    lookup = requests.post(
        f"{settings.KHALTI_BASE_URL}/epayment/lookup/",
        headers=headers,
        json={"pidx": pidx}
    )
    lookup_data = lookup.json()
    
    if lookup_data.get('status') == 'Completed':
        appointment.payment_status = 'completed'
        appointment.status = 'scheduled'
        appointment.save()
        return render(request, 'appointment/appointment_success.html', context)
```

### eSewa Callback (`esewa_callback`)
eSewa sends the response base64 encoded as a query parameter `?data=...`.
```python
def esewa_callback(request):
    encoded_data = request.GET.get('data', '')
    decoded = base64.b64decode(encoded_data).decode('utf-8')
    response = json.loads(decoded)
    
    # Re-verify the signature eSewa sent back
    signed_fields = response.get('signed_field_names', '').split(',')
    sign_message = ','.join(f"{f}={response.get(f, '')}" for f in signed_fields if f != 'signature')
    expected_sig = _generate_esewa_signature(settings.ESEWA_SECRET_KEY, sign_message)
    
    if expected_sig == response.get('signature') and response.get('status') == 'COMPLETE':
        appointment = Appointment.objects.get(khalti_pidx=response['transaction_uuid'])
        appointment.payment_status = 'completed'
        appointment.status = 'scheduled'
        appointment.save()
        return render(request, 'appointment/appointment_success.html', context)
```

## Summary
By keeping business logic inside the backend (`views.py`), the secret keys are never exposed to the client's browser, making the integration secure.

---

---

# Email / SMTP Integration

This section explains how real email sending (Gmail SMTP) was added to the project, replacing the previous "console backend" that only printed emails to the terminal. Every file that was changed is explained below.

---

## 1. What Was There Before (Console Backend)

Before this implementation, Django was configured like this in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This setting means **Django never actually sends any email**. Instead, it prints the full email content (To, Subject, Body) directly in the terminal window where the server is running. This is useful during development to see what would be sent, but it means no real user ever receives an email.

There was also a file `appointments/email_utils.py` with 4 functions that had `send_mail()` calls commented out with a `# TODO: Uncomment when SMTP is configured` comment. These functions only called `_print_email_to_terminal()`, which again just printed to the terminal.

---

## 2. Changes Made — File by File

---

### File 1: `.env` (Credentials Added by Developer)

The `.env` file stores secret credentials that should never be hardcoded in code or pushed to GitHub.

**Added lines:**
```env
# Email / SMTP
EMAIL_HOST_USER='your_gmail@gmail.com'
EMAIL_HOST_PASSWORD='your_16_character_app_password'
```

- `EMAIL_HOST_USER` — the Gmail account that sends all emails from the app
- `EMAIL_HOST_PASSWORD` — a **16-character App Password** generated from Google Account settings (NOT your Gmail login password). App Passwords are created at: `Google Account → Security → 2-Step Verification → App Passwords`

> **Why not use the real Gmail password?** Google blocks direct SMTP login with your real password for security. App Passwords are specifically designed for apps.

---

### File 2: `myproject/settings.py` (Email Backend Switch)

**Before:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**After:**
```python
# ── Email / SMTP ────────────────────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL  = os.getenv('EMAIL_HOST_USER')
```

**What each line does:**

| Setting | Purpose |
|---------|---------|
| `EMAIL_BACKEND` | Tells Django to use real SMTP instead of just printing to terminal |
| `EMAIL_HOST` | The SMTP server address. Gmail's is `smtp.gmail.com` |
| `EMAIL_PORT` | Port 587 is the standard port for TLS-encrypted SMTP |
| `EMAIL_USE_TLS` | Enables TLS encryption so the email is sent securely |
| `EMAIL_HOST_USER` | The Gmail address that sends the email. Reads from `.env` |
| `EMAIL_HOST_PASSWORD` | The App Password. Reads from `.env`. Never hardcoded |
| `DEFAULT_FROM_EMAIL` | The "From:" address that appears in the recipient's inbox |

**Why use `os.getenv()`?**
`os.getenv('KEY')` reads the value from the `.env` file (loaded by `python-dotenv`). This means the actual credentials are never written directly in the code, so they can't be accidentally pushed to GitHub.

**Allauth settings also updated:**
```python
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_VERIFICATION = 'none'
```
- `ACCOUNT_SIGNUP_FIELDS` — tells allauth that email and password are required fields when signing up
- `ACCOUNT_LOGIN_METHODS` — users log in using email (not username)
- `ACCOUNT_EMAIL_VERIFICATION = 'none'` — disables allauth's own email verification step. This is set to `'none'` because users who sign up via Google or Facebook already have verified emails from those providers

---

### File 3: `appointments/email_utils.py` (Main Email Functions)

This file contains all the email templates and sending logic for appointment-related emails.

**Before:** Each function only called `_print_email_to_terminal()` and had `send_mail()` commented out.

**After:** Each function now:
1. Still calls `_print_email_to_terminal()` so the email is visible in the terminal for debugging
2. **Also** calls `send_mail()` to actually send the real email via Gmail SMTP

**Import added at top of file:**
```python
from django.core.mail import send_mail
from django.conf import settings
```
- `send_mail` is Django's built-in function to send an email using whatever backend is configured in `settings.py`
- `settings` is imported so we can read `settings.DEFAULT_FROM_EMAIL` dynamically instead of hardcoding an address

#### Function 1: `send_appointment_confirmation_email(appointment)`

**Purpose:** Sends a confirmation email to the patient right after they successfully book an appointment.

**Code added:**
```python
send_mail(
    subject,
    body,
    settings.DEFAULT_FROM_EMAIL,  # From: subedianish937@gmail.com
    [appointment.email],           # To: patient's email
    fail_silently=False,
)
```

- `subject` — e.g. "Appointment Confirmed with Dr. John Smith"
- `body` — the full email text with appointment date, time, doctor name, etc.
- `settings.DEFAULT_FROM_EMAIL` — uses the Gmail credentials from `.env`
- `[appointment.email]` — sends to the email the patient entered in the booking form
- `fail_silently=False` — if SMTP fails, it raises an error instead of silently ignoring it

#### Function 2: `send_video_call_link_email(appointment)`

**Purpose:** Sends the video call URL and access code to the patient when the doctor clicks "Send Video Call Link" in the DoctorAdmin panel.

**Code added:** Same `send_mail()` pattern as above. The body includes the `appointment.video_call_link` and `appointment.call_access_code` fields.

#### Function 3: `send_appointment_reminder_email(appointment)`

**Purpose:** Sends a reminder email 24 hours before the appointment. This function is ready to send real emails, but it needs a **scheduled task (cron job)** to automatically call it at the right time. That is a separate future implementation.

**Code added:** Same `send_mail()` pattern.

#### Function 4: `send_appointment_cancelled_email(appointment, cancelled_by='patient')`

**Purpose:** Sends a cancellation notice to the patient when a payment is cancelled or fails.

**Important:** This function had **no `send_mail()` call at all** before — not even a commented-out one. One was added from scratch:

```python
send_mail(
    subject,
    body,
    settings.DEFAULT_FROM_EMAIL,
    [appointment.email],
    fail_silently=False,
)
```

---

### File 4: `appointments/views.py` (Triggering Emails at the Right Moment)

Previously the email functions were defined in `email_utils.py` but were **never called** from the views. This file wires everything together.

**Import added at top:**
```python
import logging
from .email_utils import (
    send_appointment_confirmation_email,
    send_appointment_cancelled_email,
)

logger = logging.getLogger(__name__)
```

- `logging` is Python's standard logging library. We use it to record errors to the server log without crashing the user's page.
- `logger.error(...)` saves error messages to the server log. This is important for payment callbacks — if SMTP fails, the patient should still see their success page.

**Why wrap in `try/except`?**
Each email call is wrapped like this:
```python
try:
    send_appointment_confirmation_email(appointment)
except Exception as e:
    logger.error(f"Failed to send confirmation email for appointment {appointment.id}: {e}")
```
If Gmail is temporarily down or credentials expire, the `except` block catches the error and logs it. The payment success page still renders normally. Without this, a broken SMTP would crash the entire payment callback and confuse the user.

#### Trigger Point 1: Non-payment booking (`save_appointment` view)
When a patient books without Khalti or eSewa (e.g. pay at clinic), the appointment goes straight to `status = 'scheduled'`. Confirmation email is now sent here:
```python
# Send confirmation email
try:
    send_appointment_confirmation_email(appointment)
except Exception as e:
    logger.error(...)

messages.success(request, "🎉 Appointment confirmed...")
return redirect('home')
```

#### Trigger Point 2: Khalti payment success (`khalti_callback` view)
After verifying payment with Khalti's Lookup API and confirming `status == 'Completed'`:
```python
appointment.payment_status = 'completed'
appointment.status = 'scheduled'
appointment.save()

# Send confirmation email to patient
try:
    send_appointment_confirmation_email(appointment)
except Exception as e:
    logger.error(...)
```

#### Trigger Point 3: eSewa payment success (`esewa_callback` view)
After verifying eSewa's signature and confirming `status == 'COMPLETE'`:
```python
appointment.payment_status = 'completed'
appointment.status = 'scheduled'
appointment.save()

# Send confirmation email to patient
try:
    send_appointment_confirmation_email(appointment)
except Exception as e:
    logger.error(...)
```

#### Trigger Point 4: Khalti payment cancelled
When Khalti sends back `status == 'User canceled'`:
```python
appointment.payment_status = 'failed'
appointment.status = 'cancelled'
appointment.save()

try:
    send_appointment_cancelled_email(appointment, cancelled_by='patient')
except Exception as e:
    logger.error(...)
```

---

### File 5: `pages/views.py` (Contact Us Form — New Feature)

**Before:** `ContactUsView` only had a `get()` method that rendered the template. The form never did anything when submitted.

**After:** A `post()` method was added that reads the form fields and sends an email.

**Imports added:**
```python
from django.core.mail import EmailMessage, BadHeaderError
from django.conf import settings
```

Why `EmailMessage` instead of `send_mail`? Because `EmailMessage` supports the `reply_to` parameter. This means when the DocPlus team replies to the contact email in Gmail, the reply goes directly to the visitor who contacted them — not back to the DocPlus Gmail itself.

**The `post()` method logic:**
```python
def post(self, request):
    # 1. Read form fields
    full_name = request.POST.get('full_name', '').strip()
    email     = request.POST.get('email', '').strip()
    subject   = request.POST.get('subject', '').strip()
    message   = request.POST.get('message', '').strip()

    # 2. Basic validation — all required fields must be filled
    if not all([full_name, email, subject, message]):
        messages.error(request, 'Please fill in all required fields.')
        return render(request, 'contact_us/contact_us.html')

    # 3. Build the email
    msg = EmailMessage(
        subject=f"[DocPlus Contact] {subject} — from {full_name}",
        body=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,   # Sent from DocPlus Gmail
        to=[settings.EMAIL_HOST_USER],             # Received in DocPlus Gmail inbox
        reply_to=[email],                          # Replying goes to the visitor
    )
    msg.send(fail_silently=False)
```

---

### File 6: `pages/templates/contact_us/contact_us.html` (Form Fixed)

**Before:** The HTML form had no `method`, no `action`, and no `name` attributes on any input field. This means when the user clicked "Send Message", the browser did nothing useful — there was no way to receive the data in Django.

**Changes made:**

```html
<!-- BEFORE -->
<form>
    <input type="text" placeholder="Your name">
    <input type="email" placeholder="your@email.com">
    <select>...</select>
    <textarea placeholder="..."></textarea>
```

```html
<!-- AFTER -->
<form method="post" action="{% url 'contact_us' %}">
    {% csrf_token %}
    <input type="text" name="full_name" placeholder="Your name" required>
    <input type="email" name="email" placeholder="your@email.com" required>
    <select name="subject" required>...</select>
    <textarea name="message" placeholder="..." required></textarea>
```

| Change | Why |
|--------|-----|
| `method="post"` | Tells the browser to send data to the server when submitted |
| `action="{% url 'contact_us' %}"` | Specifies which URL/view receives the form data |
| `{% csrf_token %}` | Django security requirement — prevents Cross-Site Request Forgery attacks. Django will reject any POST without this |
| `name="full_name"` etc. | Without a `name` attribute, the browser does not include the field in the POST data. Django reads form data by field name |
| `required` | HTML-level validation — browser shows an error if field is empty before submitting |

A messages block was also added inside the form to show success/error feedback:
```html
{% if messages %}
    {% for message in messages %}
        <div class="alert ...">{{ message }}</div>
    {% endfor %}
{% endif %}
```

---

## 3. How Django's Password Reset Works (Auto-Fixed by settings.py)

Django has a built-in password reset system that was already set up in `accounts/urls.py`. The 4-step flow is:

```
Step 1: /password-reset/
  → User enters their email address
  → Django calls PasswordResetView

Step 2: Django sends an email using EMAIL_BACKEND
  → Email contains a unique one-time reset link
  → Template: accounts/templates/forget_password/password_reset_email.html

Step 3: /password-reset-confirm/<uidb64>/<token>/
  → User clicks link from email
  → User enters new password

Step 4: /password-reset-complete/
  → Password changed successfully
```

**Before SMTP:** Step 2 printed the reset link to the terminal. The user could never receive it.

**After SMTP:** Step 2 sends a real email to the user's inbox. No code changes were needed — simply changing `EMAIL_BACKEND` in `settings.py` was enough.

---

## 4. Step-by-Step: What You Need to Do to Make SMTP Work

Follow these steps in order. Missing any one step will break email sending.

---

### Step 1 — Enable 2-Factor Authentication on Gmail
1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google", click **2-Step Verification**
4. Follow the steps to enable it (required before you can create App Passwords)

---

### Step 2 — Create a Gmail App Password
1. In the same Security page, search for **App Passwords**
2. Select **App** → "Mail" and **Device** → "Other (Custom name)" → type "DocPlus"
3. Click **Generate**
4. Copy the 16-character password shown (e.g. `nbrd mnye mqdr brrh`)

> This password is only shown once. Save it immediately.

---

### Step 3 — Add Credentials to `.env`
Open the `.env` file in the project root and add:
```env
EMAIL_HOST_USER='your_gmail@gmail.com'
EMAIL_HOST_PASSWORD='your 16 character app password'
```

---

### Step 4 — Update `settings.py`
Replace the old console backend with the following SMTP block:
```python
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL  = os.getenv('EMAIL_HOST_USER')
```

---

### Step 5 — Install Dependencies (if not already)
```bash
pip install python-dotenv
```
This library reads `.env` files. `load_dotenv()` must be called at the top of `settings.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

### Step 6 — Update `email_utils.py`
In each email function, add the real `send_mail()` call:
```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject,
    body,
    settings.DEFAULT_FROM_EMAIL,
    [recipient_email],
    fail_silently=False,
)
```

---

### Step 7 — Call Email Functions from Views
Import the email functions and call them at the right moment in `views.py`:
```python
from .email_utils import send_appointment_confirmation_email

# Inside khalti_callback, after appointment.save():
try:
    send_appointment_confirmation_email(appointment)
except Exception as e:
    logger.error(f"Email failed: {e}")
```

---

### Step 8 — Fix the Contact Us HTML Form
Add `method`, `action`, `name` attributes, and CSRF token:
```html
<form method="post" action="{% url 'contact_us' %}">
    {% csrf_token %}
    <input type="text" name="full_name" required>
    <input type="email" name="email" required>
    <select name="subject" required>...</select>
    <textarea name="message" required></textarea>
    <button type="submit">Send Message</button>
</form>
```

---

### Step 9 — Add POST Handler to ContactUsView
```python
# pages/views.py
from django.core.mail import EmailMessage, BadHeaderError

class ContactUsView(View):
    def get(self, request):
        return render(request, 'contact_us/contact_us.html')

    def post(self, request):
        full_name = request.POST.get('full_name', '').strip()
        email     = request.POST.get('email', '').strip()
        subject   = request.POST.get('subject', '').strip()
        message   = request.POST.get('message', '').strip()

        msg = EmailMessage(
            subject=f"[DocPlus Contact] {subject} — {full_name}",
            body=f"From: {full_name}\nEmail: {email}\n\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.EMAIL_HOST_USER],
            reply_to=[email],
        )
        msg.send(fail_silently=False)
        messages.success(request, 'Message sent!')
        return redirect('contact_us')
```

---

### Step 10 — Test SMTP is Working
Run this command in your terminal (with the virtual environment activated):
```bash
python manage.py sendtestemail your_email@gmail.com
```
If you receive a test email in your inbox, SMTP is configured correctly.

---

### Step 11 — Verify No Issues
```bash
python manage.py check
```
Should output: `System check identified no issues (0 silenced).`

---

## 5. URL Configuration (How Views Connect to URLs)

For any view to receive requests, it must be registered in `urls.py`. The Contact Us view is already registered in `pages/urls.py`:

```python
# pages/urls.py
from django.urls import path
from .views import ContactUsView

urlpatterns = [
    path('contact-us/', ContactUsView.as_view(), name='contact_us'),
]
```

**How it works:**
1. User visits `http://localhost:8000/contact-us/` → browser sends a **GET** request
2. Django finds `path('contact-us/', ...)` in `urls.py` → routes to `ContactUsView`
3. Since it's a GET request → `ContactUsView.get()` is called → renders the HTML form
4. User fills form and clicks Submit → browser sends a **POST** request to the same URL
5. Django routes to `ContactUsView` again → sees it's a POST → calls `ContactUsView.post()`
6. `post()` reads form fields, sends email, redirects with success message

The `name='contact_us'` in the URL pattern is what `{% url 'contact_us' %}` in the HTML template refers to. This way if the URL path ever changes, only `urls.py` needs updating — not every template.

**The project-level `urls.py` (`myproject/urls.py`) includes the pages URLs:**
```python
# myproject/urls.py
from django.urls import path, include

urlpatterns = [
    path('', include('pages.urls')),      # includes contact_us, home, etc.
    path('', include('accounts.urls')),   # includes login, register, password reset
    path('appointments/', include('appointments.urls')),
    # ... other apps
]
```

This is the "main router" — it delegates to each app's own `urls.py`.
