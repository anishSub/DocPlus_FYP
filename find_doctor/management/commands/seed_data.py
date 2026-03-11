import os
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.base import ContentFile
from faker import Faker
from PIL import Image
from io import BytesIO

# Import your models
from find_hospital.models import Hospital, Service, Department, HospitalReview
from find_doctor.models import DoctorProfile, DoctorSchedule, DoctorReview

User = get_user_model()
fake = Faker()

# ─── Seed Credentials ────────────────────────────────────────────────────────
HOSPITAL_ADMIN_PASSWORD = "hospital123"   # password for ALL hospital admin accounts
DOCTOR_PASSWORD         = "doctor123"     # password for ALL doctor accounts

# ─── Doctor seed data ────────────────────────────────────────────────────────
POSITIONS = [
    'Senior Consultant', 'Consultant', 'Associate Professor',
    'Assistant Professor', 'Resident Doctor', 'Chief of Surgery',
    'Head of Department', 'Medical Officer',
]

LANGUAGES = [
    ['Nepali', 'English'],
    ['Nepali', 'English', 'Hindi'],
    ['Nepali', 'Hindi'],
    ['Nepali', 'English', 'Maithili'],
]

BIOS = [
    "Dedicated physician with a passion for patient-centered care and evidence-based medicine.",
    "Experienced specialist committed to providing high-quality healthcare to the people of Nepal.",
    "Board-certified doctor with expertise in advanced diagnostic and therapeutic procedures.",
    "Compassionate medical professional focused on holistic patient wellness and recovery.",
    "Specialist with extensive research background and clinical experience across leading institutions.",
]

REVIEW_COMMENTS = [
    "Excellent doctor, very thorough and professional.",
    "Highly recommended. Listened patiently and explained clearly.",
    "Good consultation. Prescribed appropriate medication.",
    "Very experienced and knowledgeable specialist.",
    "Kind and compassionate. Will visit again.",
    "Quick diagnosis and effective treatment plan.",
    "Great bedside manner. Highly skilled professional.",
]

HOSPITAL_REVIEW_COMMENTS = [
    "Clean facilities and very professional staff.",
    "Excellent hospital with state-of-the-art equipment.",
    "Short waiting times and knowledgeable doctors.",
    "Good hospital but parking is limited.",
    "Very organised and well-maintained hospital.",
    "Great emergency services, quick response.",
    "Highly recommended for specialist consultations.",
]


class Command(BaseCommand):
    help = 'Seeds database with Real Nepal Hospitals, Doctors, and Reviews'

    def get_local_image(self, folder_name, backup_color, prefix):
        """Fetch a random local image or fall back to a solid-colour placeholder."""
        base_folder = os.path.join(settings.BASE_DIR, 'seed_images', folder_name)

        if os.path.exists(base_folder):
            images = [
                f for f in os.listdir(base_folder)
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))
            ]
            if images:
                selected_image = random.choice(images)
                with open(os.path.join(base_folder, selected_image), 'rb') as f:
                    return ContentFile(f.read(), name=selected_image)

        # Fallback: generate a solid-colour placeholder
        image = Image.new('RGB', (800, 600), color=backup_color)
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        return ContentFile(
            buffer.getvalue(),
            name=f'{prefix}_{random.randint(1000, 9999)}.jpg',
        )

    def generate_dummy_pdf(self, name):
        return ContentFile(b"Dummy PDF content", name=f'{name}.pdf')

    # ─────────────────────────────────────────────────────────────────────────
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 65))
        self.stdout.write(self.style.MIGRATE_HEADING("  DocPlus Database Seeder"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 65))

        # ── 1. Services & Departments ─────────────────────────────────────
        service_names = [
            'ICU', 'Emergency', 'X-Ray', 'MRI', 'Pharmacy',
            'Ambulance', 'Blood Bank', 'Cafeteria', 'Ventilator',
        ]
        dept_names = [
            'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics',
            'Dermatology', 'Oncology', 'ENT', 'Gynecology', 'General Surgery',
        ]

        db_services = [Service.objects.get_or_create(name=n)[0] for n in service_names]
        db_departments = [Department.objects.get_or_create(name=n)[0] for n in dept_names]

        # ── 2. Hospitals ──────────────────────────────────────────────────
        real_hospitals = [
            # Bagmati (Kathmandu)
            {"name": "Bir Hospital",                            "city": "Kathmandu",  "type": "General",          "beds": 500},
            {"name": "Tribhuvan University Teaching Hospital",  "city": "Kathmandu",  "type": "Teaching",         "beds": 700},
            {"name": "Norvic International Hospital",           "city": "Kathmandu",  "type": "Multi-Specialty",  "beds": 150},
            {"name": "Grande International Hospital",           "city": "Kathmandu",  "type": "Super-Specialty",  "beds": 200},
            # Gandaki (Pokhara)
            {"name": "Manipal Teaching Hospital",               "city": "Pokhara",    "type": "Teaching",         "beds": 750},
            {"name": "Gandaki Medical College",                 "city": "Pokhara",    "type": "Teaching",         "beds": 500},
            {"name": "Charak Memorial Hospital",                "city": "Pokhara",    "type": "Multi-Specialty",  "beds": 100},
            # Koshi Province
            {"name": "B.P. Koirala Institute of Health Sciences","city": "Dharan",   "type": "Teaching",         "beds": 800},
            {"name": "Nobel Medical College",                   "city": "Biratnagar", "type": "Teaching",         "beds": 600},
            # Lumbini
            {"name": "Lumbini Provincial Hospital",             "city": "Butwal",     "type": "General",          "beds": 300},
            # Chitwan
            {"name": "Bharatpur Hospital",                      "city": "Bharatpur",  "type": "General",          "beds": 600},
            {"name": "College of Medical Sciences",             "city": "Bharatpur",  "type": "Teaching",         "beds": 500},
            # Sudurpashchim
            {"name": "Seti Provincial Hospital",                "city": "Dhangadhi",  "type": "General",          "beds": 125},
        ]

        # ── Print Hospital Admin credential header ────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("  Hospital Admin Credentials"))
        self.stdout.write(self.style.MIGRATE_HEADING(f"  Password for ALL hospital admins: {HOSPITAL_ADMIN_PASSWORD}"))
        self.stdout.write(self.style.MIGRATE_HEADING("  " + "-" * 61))
        self.stdout.write(f"  {'#':<4} {'Email':<50} {'Hospital Name'}")
        self.stdout.write("  " + "-" * 90)

        created_hospitals = []

        for idx, h_data in enumerate(real_hospitals, start=1):
            slug  = h_data['name'].lower().replace(' ', '').replace('.', '')
            email = f"contact@{slug}.com"

            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=HOSPITAL_ADMIN_PASSWORD,
                    role='HOSPITAL_ADMIN',
                )

                h_image = self.get_local_image('hospital', (128, 128, 128), 'hospital_gen')

                hospital = Hospital.objects.create(
                    user=user,
                    name=h_data['name'],
                    hospital_type=h_data['type'],
                    established_year=fake.date_between(start_date='-30y', end_date='-5y'),
                    phone=fake.numerify('+977 01-#######'),
                    email=email,
                    city=h_data['city'],
                    district=h_data['city'],
                    address=f"{h_data['city']}, Nepal",
                    website=f"https://www.{slug}.com.np",
                    # ← appointment_link was missing
                    appointment_link=f"https://www.{slug}.com.np/appointment",
                    total_beds=h_data['beds'],
                    description=(
                        f"{h_data['name']} is a leading healthcare provider in "
                        f"{h_data['city']}, offering state-of-the-art medical services."
                    ),
                    image=h_image,
                    emergency_available=True,
                    opd_start="09:00",
                    opd_end="17:00",
                    achievements="Best Hospital Award 2024",
                    is_verified=True,
                    # analytics fields — defaults are 0, set a small random seed value
                    total_views=random.randint(100, 5000),
                    total_website_clicks=random.randint(10, 500),
                )

                hospital.services.set(random.sample(db_services, k=random.randint(4, 8)))
                hospital.departments.set(random.sample(db_departments, k=random.randint(3, 6)))
                created_hospitals.append(hospital)

                self.stdout.write(f"  {idx:<4} {email:<50} {h_data['name']}")
            else:
                try:
                    hospital = Hospital.objects.get(name=h_data['name'])
                    created_hospitals.append(hospital)
                    self.stdout.write(f"  {idx:<4} {'(already exists)':<50} {h_data['name']}")
                except Hospital.DoesNotExist:
                    pass

        # ── 3. Doctors ────────────────────────────────────────────────────
        specialties = [
            'Cardiologist', 'Dermatologist', 'Neurologist',
            'Pediatrician', 'Orthopedist', 'General Surgeon',
            'Ophthalmologist', 'Gynecologist', 'ENT Specialist', 'Psychiatrist',
        ]

        if not created_hospitals:
            self.stdout.write(self.style.ERROR("No hospitals found or created. Cannot create doctors."))
            return

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("  Doctor Credentials"))
        self.stdout.write(self.style.MIGRATE_HEADING(f"  Password for ALL doctors: {DOCTOR_PASSWORD}"))
        self.stdout.write(self.style.MIGRATE_HEADING("  " + "-" * 61))
        self.stdout.write(f"  {'#':<4} {'Email':<45} {'Name':<25} {'Specialty'}")
        self.stdout.write("  " + "-" * 105)

        created_doctors = []

        # Hardcoded list — emails are ALWAYS predictable (no Faker randomness)
        DOCTORS = [
            {"first": "Rajesh",   "last": "Sharma",     "gender": "Male"},
            {"first": "Priya",    "last": "Thapa",       "gender": "Female"},
            {"first": "Suresh",   "last": "Adhikari",    "gender": "Male"},
            {"first": "Anita",    "last": "Karki",       "gender": "Female"},
            {"first": "Bikash",   "last": "Poudel",      "gender": "Male"},
            {"first": "Sita",     "last": "Shrestha",    "gender": "Female"},
            {"first": "Nabin",    "last": "Bhattarai",   "gender": "Male"},
            {"first": "Sunita",   "last": "Rai",         "gender": "Female"},
            {"first": "Dipak",    "last": "Pandey",      "gender": "Male"},
            {"first": "Kopila",   "last": "Basnet",      "gender": "Female"},
            {"first": "Roshan",   "last": "Koirala",     "gender": "Male"},
            {"first": "Sabina",   "last": "Tamang",      "gender": "Female"},
            {"first": "Saroj",    "last": "Maharjan",    "gender": "Male"},
            {"first": "Kamala",   "last": "Gurung",      "gender": "Female"},
            {"first": "Prabhat",  "last": "Devkota",     "gender": "Male"},
            {"first": "Manisha",  "last": "Acharya",     "gender": "Female"},
            {"first": "Aashish",  "last": "Joshi",       "gender": "Male"},
            {"first": "Rupa",     "last": "Magar",       "gender": "Female"},
            {"first": "Santosh",  "last": "Upreti",      "gender": "Male"},
            {"first": "Nisha",    "last": "Lama",        "gender": "Female"},
            {"first": "Binod",    "last": "Khanal",      "gender": "Male"},
            {"first": "Kabita",   "last": "Subedi",      "gender": "Female"},
            {"first": "Deepak",   "last": "Ghimire",     "gender": "Male"},
            {"first": "Samjhana", "last": "Dahal",       "gender": "Female"},
            {"first": "Mahesh",   "last": "Humagain",    "gender": "Male"},
            {"first": "Barsha",   "last": "Neupane",     "gender": "Female"},
            {"first": "Sagar",    "last": "Bhandari",    "gender": "Male"},
            {"first": "Saraswati","last": "Parajuli",    "gender": "Female"},
            {"first": "Nirajan",  "last": "Chaudhary",   "gender": "Male"},
            {"first": "Anju",     "last": "Ale",         "gender": "Female"},
        ]

        for i, doc in enumerate(DOCTORS):
            first_name  = doc["first"]
            last_name   = doc["last"]
            gender_code = doc["gender"]
            folder      = 'male' if gender_code == 'Male' else 'female'
            color       = (100, 149, 237) if gender_code == 'Male' else (255, 182, 193)

            email         = f"dr.{first_name.lower()}.{last_name.lower()}{i}@docplus.com"
            specialty     = random.choice(specialties)
            assigned_hosp = random.choice(created_hospitals)


            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=DOCTOR_PASSWORD,
                    first_name=first_name,
                    last_name=last_name,
                )
                # Force the role to DOCTOR (bypasses the save() overwrite)
                user.role = User.Role.DOCTOR
                user.save(update_fields=['role'])

                photo_file = self.get_local_image(folder, color, f"doc_{gender_code[:1]}")

                doctor = DoctorProfile.objects.create(
                    user=user,
                    # Personal
                    mobile_number=fake.numerify('+977 98########'),
                    date_of_birth=fake.date_of_birth(minimum_age=28, maximum_age=60).strftime('%Y-%m-%d'),
                    gender=gender_code,
                    city=assigned_hosp.city,
                    address=f"{assigned_hosp.city}, Nepal",
                    profile_photo=photo_file,
                    # Professional
                    specialization=specialty,
                    sub_specialty=random.choice([
                        'Interventional', 'Pediatric', 'Surgical',
                        'Diagnostic', 'Clinical', '',
                    ]),
                    license_number=f"NMC-{random.randint(10000, 99999)}",
                    registration_number=f"REG-{random.randint(10000, 99999)}",
                    registration_council="Nepal Medical Council",
                    years_of_experience=random.randint(2, 25),
                    current_position=random.choice(POSITIONS),
                    languages_spoken=random.choice(LANGUAGES),
                    # Hospital
                    hospital_affiliation=assigned_hosp,
                    hospital_name_manual=assigned_hosp.name,
                    # Education & Fees
                    medical_degree=random.choice(['MBBS, MD', 'MBBS, MS', 'MBBS, DM', 'MBBS, MCh']),
                    medical_school=random.choice([
                        'Tribhuvan University', 'Kathmandu University',
                        'BP Koirala Institute', 'Manipal College of Medical Sciences',
                        'Nobel Medical College',
                    ]),
                    graduation_year=random.randint(2000, 2018),
                    consultation_fee=random.choice([500, 800, 1000, 1200, 1500, 2000]),
                    # Schedule
                    available_days=random.choice([
                        ['Sun', 'Mon', 'Tue', 'Wed', 'Thu'],
                        ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                        ['Sun', 'Mon', 'Wed', 'Thu', 'Fri'],
                        ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
                    ]),
                    available_time_start='09:00',
                    available_time_end='17:00',
                    bio=random.choice(BIOS),
                    # Documents
                    cv=self.generate_dummy_pdf('cv'),
                    medical_license_doc=self.generate_dummy_pdf('license'),
                    degree_certificate=self.generate_dummy_pdf('degree'),
                    # Flags
                    is_approved=True,
                    enable_video_consultations=True,
                    auto_accept_appointments=random.choice([True, False]),
                )

                # Per-day DoctorSchedule rows
                for day in doctor.available_days:
                    DoctorSchedule.objects.create(
                        doctor=doctor,
                        day=day,
                        start_time='09:00',
                        end_time='17:00',
                    )

                created_doctors.append((email, first_name, last_name, specialty))
                self.stdout.write(
                    f"  {i+1:<4} {email:<45} "
                    f"Dr. {first_name} {last_name:<20} {specialty}"
                )

        # ── 4. Doctor Reviews ─────────────────────────────────────────────
        reviewer_pool = list(User.objects.filter(role='HOSPITAL_ADMIN')[:10])
        if reviewer_pool:
            self.stdout.write("\n  Adding doctor reviews...")
            for doctor_profile in DoctorProfile.objects.filter(is_approved=True):
                reviewers = random.sample(reviewer_pool, min(random.randint(3, 5), len(reviewer_pool)))
                for reviewer in reviewers:
                    DoctorReview.objects.get_or_create(
                        user=reviewer,
                        doctor=doctor_profile,
                        defaults={
                            'rating':      random.randint(3, 5),
                            'comment':     random.choice(REVIEW_COMMENTS),
                            'is_approved': True,
                        },
                    )

        # ── 5. Hospital Reviews ───────────────────────────────────────────
        doctor_users = list(User.objects.filter(role='DOCTOR')[:15])
        if doctor_users:
            self.stdout.write("  Adding hospital reviews...")
            for hospital in created_hospitals:
                reviewers = random.sample(doctor_users, min(random.randint(3, 5), len(doctor_users)))
                for reviewer in reviewers:
                    HospitalReview.objects.get_or_create(
                        user=reviewer,
                        hospital=hospital,
                        defaults={
                            'rating':      random.randint(3, 5),
                            'comment':     random.choice(HOSPITAL_REVIEW_COMMENTS),
                            'is_approved': True,
                        },
                    )

        # ── 6. Final Summary ──────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 65))
        self.stdout.write(self.style.SUCCESS(
            f"  ✅ Seeding complete!\n\n"
            f"  Hospitals seeded  : {len(created_hospitals)}\n"
            f"  Doctors seeded    : {len(created_doctors)}\n\n"
            f"  ── Hospital Admins ──────────────────────────────\n"
            f"  Email format : contact@<hospitalname>.com\n"
            f"  Password     : {HOSPITAL_ADMIN_PASSWORD}\n"
            f"  Login URL    : /accounts/login/\n\n"
            f"  ── Doctors ──────────────────────────────────────\n"
            f"  Email format : dr.<firstname>.<lastname>N@docplus.com\n"
            f"  Password     : {DOCTOR_PASSWORD}\n"
            f"  Login URL    : /accounts/login/"
        ))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 65))