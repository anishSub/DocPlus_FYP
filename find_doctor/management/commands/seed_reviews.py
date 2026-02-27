"""
Management command: seed_reviews
Usage:   python manage.py seed_reviews
Purpose: Seeds fake patient users and realistic ratings for ALL existing
         DoctorProfile and Hospital objects — without touching the doctors
         or hospitals themselves.

Run seed_data.py first, then run this.
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from accounts.models import PatientProfile
from find_doctor.models import DoctorProfile, DoctorReview
from find_hospital.models import Hospital, HospitalReview

User = get_user_model()

# ── Constants ─────────────────────────────────────────────────────────────────
PATIENT_PASSWORD = "patient123"
NUM_PATIENTS     = 25   # fake patient accounts to create

# Weighted rating pool — more 4s & 5s, some 3s, a few 1–2s (realistic)
RATING_POOL = [5, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 2, 2, 1]

DOCTOR_COMMENTS = [
    "Excellent doctor! Very thorough and professional.",
    "Highly recommended. Listened patiently and explained everything clearly.",
    "Good consultation. Prescribed appropriate medication.",
    "Very experienced and knowledgeable. Felt at ease throughout.",
    "Kind and compassionate doctor. Will definitely visit again.",
    "Quick to diagnose and had an effective treatment plan.",
    "Great bedside manner. Highly skilled professional.",
    "Average experience. Wait time was long.",
    "Doctor was knowledgeable but seemed rushed during consultation.",
    "Not very satisfied. Could improve communication with patients.",
    "Brilliant doctor. Saved me a lot of worry with a clear explanation.",
    "Very informative session. All my questions were answered.",
    "Felt a bit rushed but the diagnosis was accurate.",
    "Wonderful doctor — goes above and beyond for patients.",
    "Good overall but the appointment started late.",
    "Highly professional and caring. Best doctor I have visited.",
    "Average. The consultation was short.",
    "Very poor experience. Doctor did not listen properly.",
    "Outstanding specialist! Clear, concise, and very helpful.",
    "Fairly good. Would recommend to others.",
]

HOSPITAL_COMMENTS = [
    "Clean facilities and very professional staff. Highly recommend.",
    "Excellent hospital with state-of-the-art equipment.",
    "Short waiting times and knowledgeable doctors. Would visit again.",
    "Good hospital overall but parking is quite limited.",
    "Very organised and well-maintained. Staff are friendly.",
    "Great emergency services — quick response and efficient care.",
    "Highly recommended for specialist consultations.",
    "Decent hospital. Cleanliness could be improved.",
    "Average experience. Long queues at reception.",
    "Fantastic healthcare facility. Felt safe and well cared for.",
    "Staff are helpful but the waiting room is small.",
    "Good doctors but billing process is confusing.",
    "Would not recommend — waited 3 hours for a routine check.",
    "Impressive hospital. Modern equipment and skilled staff.",
    "One of the best hospitals in the region. Very satisfied.",
    "Rooms were clean and nurses were attentive.",
    "Administration could be more efficient, but overall good care.",
    "Emergency care here is excellent. Saved my life.",
    "Mediocre experience. Expected better for the cost.",
    "Wonderful staff and great facilities. Will return.",
]


class Command(BaseCommand):
    help = 'Seeds fake patient users and realistic ratings for doctors and hospitals'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 65))
        self.stdout.write(self.style.MIGRATE_HEADING("  DocPlus Review Seeder"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 65))

        # ── 1. Create fake patient users ──────────────────────────────────
        self.stdout.write("\n  Creating patient accounts...")
        patients = []

        PATIENT_NAMES = [
            ("Aarav",    "Shah"),     ("Bijay",    "Thapa"),
            ("Chandan",  "Rai"),      ("Devika",   "Karki"),
            ("Elisha",   "Poudel"),   ("Gita",     "Shrestha"),
            ("Hari",     "Adhikari"), ("Isha",     "Basnet"),
            ("Janak",    "Koirala"),  ("Kriti",    "Tamang"),
            ("Laxmi",    "Gurung"),   ("Manoj",    "Dhakal"),
            ("Nirmala",  "Acharya"),  ("Om",       "Sitoula"),
            ("Puja",     "Neupane"),  ("Rahul",    "Maharjan"),
            ("Sarita",   "Joshi"),    ("Tilak",    "Magar"),
            ("Uma",      "Upreti"),   ("Vivek",    "Lama"),
            ("Warsha",   "Khanal"),   ("Yamuna",   "Subedi"),
            ("Zeeshan",  "Ghimire"),  ("Aliva",    "Dahal"),
            ("Bikram",   "Humagain"),
        ]

        for idx, (first, last) in enumerate(PATIENT_NAMES[:NUM_PATIENTS]):
            email = f"patient{idx}@docplus.com"
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=PATIENT_PASSWORD,
                    first_name=first,
                    last_name=last,
                    role='PATIENT',
                )
                PatientProfile.objects.get_or_create(user=user)
                patients.append(user)
                self.stdout.write(f"    + {first} {last} ({email})")
            else:
                user = User.objects.get(email=email)
                patients.append(user)
                self.stdout.write(f"    – Exists: {email}")

        if not patients:
            self.stdout.write(self.style.ERROR("No patients available. Aborting."))
            return

        # ── 2. Seed Doctor Reviews ────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write("  Seeding doctor reviews...")

        all_doctors = list(DoctorProfile.objects.filter(is_approved=True))
        if not all_doctors:
            self.stdout.write(self.style.WARNING("  No approved doctors found. Run seed_data first."))
        else:
            for doctor in all_doctors:
                # Each doctor gets 4–8 patient reviews
                reviewers = random.sample(patients, min(random.randint(4, 8), len(patients)))
                for patient in reviewers:
                    DoctorReview.objects.get_or_create(
                        user=patient,
                        doctor=doctor,
                        defaults={
                            'rating':      random.choice(RATING_POOL),
                            'comment':     random.choice(DOCTOR_COMMENTS),
                            'is_approved': True,
                        },
                    )
            self.stdout.write(f"    ✔ Reviews added for {len(all_doctors)} doctors")

        # ── 3. Seed Hospital Reviews ──────────────────────────────────────
        self.stdout.write("\n  Seeding hospital reviews...")

        all_hospitals = list(Hospital.objects.filter(is_verified=True))
        if not all_hospitals:
            self.stdout.write(self.style.WARNING("  No verified hospitals found. Run seed_data first."))
        else:
            for hospital in all_hospitals:
                # Each hospital gets 5–10 patient reviews
                reviewers = random.sample(patients, min(random.randint(5, 10), len(patients)))
                for patient in reviewers:
                    HospitalReview.objects.get_or_create(
                        user=patient,
                        hospital=hospital,
                        defaults={
                            'rating':      random.choice(RATING_POOL),
                            'comment':     random.choice(HOSPITAL_COMMENTS),
                            'is_approved': True,
                        },
                    )
            self.stdout.write(f"    ✔ Reviews added for {len(all_hospitals)} hospitals")

        # ── 4. Summary ────────────────────────────────────────────────────
        from django.db.models import Avg
        doc_avg  = DoctorReview.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        hosp_avg = HospitalReview.objects.aggregate(Avg('rating'))['rating__avg'] or 0

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 65))
        self.stdout.write(self.style.SUCCESS(
            f"  ✅ Review seeding complete!\n\n"
            f"  Patients created  : {len([p for p in patients if not hasattr(p, '_existed')])}\n"
            f"  Doctor reviews    : {DoctorReview.objects.count()} total "
            f"(avg rating: {doc_avg:.2f} ⭐)\n"
            f"  Hospital reviews  : {HospitalReview.objects.count()} total "
            f"(avg rating: {hosp_avg:.2f} ⭐)\n\n"
            f"  ── Patient Login ────────────────────────────────\n"
            f"  Email    : patient0@docplus.com ... patient24@docplus.com\n"
            f"  Password : {PATIENT_PASSWORD}\n"
            f"  Login at : /accounts/login/"
        ))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 65))
