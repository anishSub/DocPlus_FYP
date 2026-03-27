import sys
import os
import django

sys.path.append('/Users/macm2/Desktop/DocPlus_FYP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

try:
    from appointments.email_utils import send_reschedule_notification_email
    print("SUCCESS")
except Exception as e:
    print("ERROR:", e)
