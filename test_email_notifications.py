"""
Automated test script to verify all email notification functions.
This script tests all email functions by printing to terminal without user input.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from appointments.models import Appointment
from appointments.email_utils import (
    send_appointment_confirmation_email,
    send_video_call_link_email,
    send_appointment_reminder_email,
    send_appointment_cancelled_email
)

def test_all_emails():
    print("\n" + "="*80)
    print("AUTOMATED EMAIL NOTIFICATION TESTING")
    print("="*80 + "\n")
    
    # Get a sample appointment
    try:
        appointment = Appointment.objects.filter(is_video_consultation=True).first()
        
        if not appointment:
            print("❌ No video consultation appointments found in database.")
            print("Please create an appointment first.")
            return
        
        print(f"✅ Testing with Appointment ID: {appointment.id}")
        print(f"   Patient: {appointment.full_name}")
        print(f"   Doctor: Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}")
        print(f"   Date: {appointment.date}")
        print(f"   Email: {appointment.email}")
        print("\n")
        
        # Test 1: Appointment Confirmation
        print("🧪 TEST 1: Appointment Confirmation Email")
        print("-" * 80)
        send_appointment_confirmation_email(appointment)
        
        # Test 2: Video Call Link
        print("\n🧪 TEST 2: Video Call Link Email")
        print("-" * 80)
        send_video_call_link_email(appointment)
        
        # Test 3: Reminder
        print("\n🧪 TEST 3: Appointment Reminder Email")
        print("-" * 80)
        send_appointment_reminder_email(appointment)
        
        # Test 4: Cancellation
        print("\n🧪 TEST 4: Appointment Cancellation Email")
        print("-" * 80)
        send_appointment_cancelled_email(appointment, cancelled_by='patient')
        
        print("\n" + "="*80)
        print("✅ ALL 4 EMAIL NOTIFICATION TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n📝 Summary:")
        print("  • Appointment Confirmation - ✅ Working")
        print("  • Video Call Link - ✅ Working")
        print("  • Appointment Reminder - ✅ Working")
        print("  • Cancellation Notice - ✅ Working")
        print("\n💡 All emails are currently printing to terminal.")
        print("   To send actual emails, configure SMTP in settings.py")
        print("   and uncomment send_mail() calls in email_utils.py\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_emails()
