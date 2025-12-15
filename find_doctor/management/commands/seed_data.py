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
from find_hospital.models import Hospital, Service, Department
from find_doctor.models import DoctorProfile

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seeds database with Real Nepal Hospitals and Doctors'

    def get_local_image(self, folder_name, backup_color, prefix):
        """Fetch local image or generate backup color."""
        base_folder = os.path.join(settings.BASE_DIR, 'seed_images', folder_name)
        
        if os.path.exists(base_folder):
            images = [f for f in os.listdir(base_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if images:
                selected_image = random.choice(images)
                with open(os.path.join(base_folder, selected_image), 'rb') as f:
                    return ContentFile(f.read(), name=selected_image)

        # Fallback
        image = Image.new('RGB', (800, 600), color=backup_color)
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        return ContentFile(buffer.getvalue(), name=f'{prefix}_{random.randint(1000,9999)}.jpg')

    def generate_dummy_pdf(self, name):
        return ContentFile(b"Dummy PDF content", name=f'{name}.pdf')

    def handle(self, *args, **kwargs):
        self.stdout.write("Started seeding data...")

        # --- 1. Create Services & Departments ---
        service_names = ['ICU', 'Emergency', 'X-Ray', 'MRI', 'Pharmacy', 'Ambulance', 'Blood Bank', 'Cafeteria', 'Ventilator']
        dept_names = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Dermatology', 'Oncology', 'ENT', 'Gynecology', 'General Surgery']

        db_services = []
        for s_name in service_names:
            obj, _ = Service.objects.get_or_create(name=s_name)
            db_services.append(obj)
        
        db_departments = []
        for d_name in dept_names:
            obj, _ = Department.objects.get_or_create(name=d_name)
            db_departments.append(obj)

        # --- 2. Real Hospital Data List ---
        real_hospitals = [
            # --- Bagmati (Kathmandu) ---
            {"name": "Bir Hospital", "city": "Kathmandu", "type": "General", "beds": 500},
            {"name": "Tribhuvan University Teaching Hospital", "city": "Kathmandu", "type": "Teaching", "beds": 700},
            {"name": "Norvic International Hospital", "city": "Kathmandu", "type": "Multi-Specialty", "beds": 150},
            {"name": "Grande International Hospital", "city": "Kathmandu", "type": "Super-Specialty", "beds": 200},
            
            # --- Gandaki (Pokhara) ---
            {"name": "Manipal Teaching Hospital", "city": "Pokhara", "type": "Teaching", "beds": 750},
            {"name": "Gandaki Medical College", "city": "Pokhara", "type": "Teaching", "beds": 500},
            {"name": "Charak Memorial Hospital", "city": "Pokhara", "type": "Multi-Specialty", "beds": 100},
            
            # --- Koshi Province (East) ---
            {"name": "B.P. Koirala Institute of Health Sciences", "city": "Dharan", "type": "Teaching", "beds": 800},
            {"name": "Nobel Medical College", "city": "Biratnagar", "type": "Teaching", "beds": 600},

            # --- Lumbini Province ---
            {"name": "Lumbini Provincial Hospital", "city": "Butwal", "type": "General", "beds": 300},
            
            # --- Chitwan (Medical Hub) ---
            {"name": "Bharatpur Hospital", "city": "Bharatpur", "type": "General", "beds": 600},
            {"name": "College of Medical Sciences", "city": "Bharatpur", "type": "Teaching", "beds": 500},

            # --- Sudurpashchim (Far West) ---
            {"name": "Seti Provincial Hospital", "city": "Dhangadhi", "type": "General", "beds": 125},
        ]

        created_hospitals = []

        for h_data in real_hospitals:
            email = f"contact@{h_data['name'].lower().replace(' ', '').replace('.', '')}.com"
            
            # Check if user exists to avoid duplicates if you run script twice
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password="password123",
                    role='HOSPITAL_ADMIN'
                )

                h_image = self.get_local_image('hospital', (128, 128, 128), 'hospital_gen')

                hospital = Hospital.objects.create(
                    user=user,
                    name=h_data['name'],
                    hospital_type=h_data['type'],
                    established_year=fake.date_between(start_date='-30y', end_date='-5y'),
                    phone=fake.phone_number(),
                    email=email,
                    city=h_data['city'],
                    district=h_data['city'], # Usually district matches city for major hubs
                    address=f"{h_data['city']}, Nepal",
                    website=f"www.{h_data['name'].lower().replace(' ', '')}.com.np",
                    
                    total_beds=h_data['beds'],
                    description=f"{h_data['name']} is a leading healthcare provider in {h_data['city']}, offering state-of-the-art medical services.",
                    
                    image=h_image,
                    emergency_available=True, # Most major hospitals have emergency
                    opd_start="09:00",
                    opd_end="17:00",
                    achievements="Best Hospital Award 2024",
                    is_verified=True
                )
                
                # Randomly assign services/departments
                hospital.services.set(random.sample(db_services, k=random.randint(4, 8)))
                hospital.departments.set(random.sample(db_departments, k=random.randint(3, 6)))
                
                created_hospitals.append(hospital)
                self.stdout.write(f"Created Hospital: {h_data['name']}")
            else:
                # If hospital exists, fetch it so we can assign doctors to it
                try:
                    hospital = Hospital.objects.get(name=h_data['name'])
                    created_hospitals.append(hospital)
                    self.stdout.write(f"Skipped (Already exists): {h_data['name']}")
                except Hospital.DoesNotExist:
                    pass

        # --- 3. Create 30 Dummy Doctors (Distributed among hospitals) ---
        specialties = ['Cardiologist', 'Dermatologist', 'Neurologist', 'Pediatrician', 'Orthopedist', 'General Surgeon']
        
        # Ensure we have hospitals to assign to
        if not created_hospitals:
            self.stdout.write(self.style.ERROR("No hospitals found or created. Cannot create doctors."))
            return

        for i in range(30):
            gender_code = random.choice(['M', 'F'])
            
            if gender_code == 'M':
                first_name = fake.first_name_male()
                last_name = fake.last_name()
                folder = 'male'
                color = (100, 149, 237)
            else:
                first_name = fake.first_name_female()
                last_name = fake.last_name()
                folder = 'female'
                color = (255, 182, 193)

            # Unique email generator
            email = f"dr.{first_name.lower()}.{last_name.lower()}{i}@docplus.com"
            
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password="password123",
                    first_name=first_name,
                    last_name=last_name,
                    role='DOCTOR'
                )
                
                photo_file = self.get_local_image(folder, color, f"doc_{gender_code}")
                
                # Randomly pick one of the created hospitals
                assigned_hospital = random.choice(created_hospitals)

                DoctorProfile.objects.create(
                    user=user,
                    mobile_number=fake.phone_number()[:15],
                    date_of_birth="1985-01-01",
                    gender=gender_code,
                    city=assigned_hospital.city, # Doctor lives in same city as hospital
                    address=f"{assigned_hospital.city}, Nepal",
                    
                    profile_photo=photo_file, 
                    cv=self.generate_dummy_pdf("cv"),
                    medical_license_doc=self.generate_dummy_pdf("license"),
                    degree_certificate=self.generate_dummy_pdf("degree"),
                    
                    specialization=random.choice(specialties),
                    license_number=f"NMC-{random.randint(1000,9999)}",
                    registration_number=f"REG-{random.randint(1000,9999)}",
                    registration_council="Nepal Medical Council",
                    years_of_experience=random.randint(2, 25),
                    
                    hospital_affiliation=assigned_hospital,
                    consultation_fee=random.choice([500, 1000, 1200, 1500, 2000]),
                    
                    medical_degree="MBBS, MD",
                    medical_school="Tribhuvan University",
                    graduation_year=random.randint(2000, 2018),
                    
                    available_days=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                    available_time_start="09:00",
                    available_time_end="17:00",
                    
                    is_approved=True
                )
                self.stdout.write(f"Created Doctor: {first_name} {last_name} at {assigned_hospital.name}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded Real Nepal Hospitals & Doctors!'))