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
