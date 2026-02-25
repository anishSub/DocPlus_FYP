"""
Management command to populate initial medical specialties
Usage: python manage.py populate_specialties
"""

from django.core.management.base import BaseCommand
from find_doctor.models import MedicalSpecialty


class Command(BaseCommand):
    help = 'Populates initial medical specialties with keywords'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating medical specialties...')
        
        specialties_data = [
            {
                'name': 'Cardiology',
                'description': 'Deals with disorders of the heart and blood vessels',
                'keywords': ['chest pain', 'heart attack', 'heart disease', 'hypertension', 'high blood pressure', 'arrhythmia', 'palpitations', 'irregular heartbeat', 'angina', 'coronary artery disease', 'heart failure', 'cardiac arrest'],
                'sub_specialties': ['Interventional Cardiology', 'Electrophysiology', 'Heart Failure'],
                'priority': 10
            },
            {
                'name': 'Neurology',
                'description': 'Focuses on disorders of the nervous system',
                'keywords': ['headache', 'migraine', 'seizure', 'epilepsy', 'stroke', 'paralysis', 'memory loss', 'dizziness', 'vertigo', 'tremor', 'parkinson', 'alzheimer', 'nerve pain', 'neuropathy', 'numbness', 'tingling'],
                'sub_specialties': ['Stroke', 'Movement Disorders', 'Epilepsy'],
                'priority': 9
            },
            {
                'name': 'Orthopedics',
                'description': 'Treats musculoskeletal system disorders',
                'keywords': ['joint pain', 'arthritis', 'fracture', 'broken bone', 'back pain', 'neck pain', 'knee pain', 'shoulder pain', 'sprain', 'ligament tear', 'sports injury', 'bone pain', 'osteoporosis', 'scoliosis'],
                'sub_specialties': ['Sports Medicine', 'Spine Surgery', 'Joint Replacement'],
                'priority': 8
            },
            {
                'name': 'Gastroenterology',
                'description': 'Deals with the digestive system and its disorders',
                'keywords': ['stomach pain', 'abdominal pain', 'diarrhea', 'constipation', 'acid reflux', 'heartburn', 'ulcer', 'gastritis', 'ibs', 'irritable bowel syndrome', 'bloating', 'nausea', 'vomiting', 'liver disease', 'hepatitis', 'jaundice'],
                'sub_specialties': ['Hepatology', 'Inflammatory Bowel Disease'],
                'priority': 8
            },
            {
                'name': 'Pulmonology',
                'description': 'Specializes in respiratory system diseases',
                'keywords': ['asthma', 'breathing difficulty', 'shortness of breath', 'cough', 'chronic cough', 'pneumonia', 'copd', 'bronchitis', 'lung disease', 'tuberculosis', 'tb', 'wheezing', 'chest congestion'],
                'sub_specialties': ['Critical Care', 'Sleep Medicine'],
                'priority': 9
            },
            {
                'name': 'Endocrinology',
                'description': 'Treats hormone-related disorders',
                'keywords': ['diabetes', 'thyroid', 'thyroid disorder', 'hormone imbalance', 'obesity', 'weight gain', 'weight loss', 'growth disorder', 'pcos', 'metabolic disorder', 'sugar', 'high sugar', 'blood sugar'],
                'sub_specialties': ['Diabetes', 'Thyroid Disorders'],
                'priority': 8
            },
            {
                'name': 'Dermatology',
                'description': 'Focuses on skin, hair, and nail conditions',
                'keywords': ['skin rash', 'acne', 'pimples', 'eczema', 'psoriasis', 'skin infection', 'hair loss', 'dandruff', 'nail problem', 'skin allergy', 'itching', 'hives', 'moles', 'warts'],
                'sub_specialties': ['Cosmetic Dermatology', 'Pediatric Dermatology'],
                'priority': 7
            },
            {
                'name': 'Nephrology',
                'description': 'Specializes in kidney-related diseases',
                'keywords': ['kidney disease', 'kidney failure', 'kidney stone', 'urinary problem', 'blood in urine', 'protein in urine', 'dialysis', 'renal failure', 'swelling', 'edema'],
                'sub_specialties': ['Dialysis', 'Kidney Transplant'],
                'priority': 8
            },
            {
                'name': 'Psychiatry',
                'description': 'Deals with mental health disorders',
                'keywords': ['depression', 'anxiety', 'stress', 'panic attack', 'bipolar', 'schizophrenia', 'ocd', 'ptsd', 'insomnia', 'sleep problem', 'mood disorder', 'mental health', 'suicidal thoughts'],
                'sub_specialties': ['Child Psychiatry', 'Addiction Medicine'],
                'priority': 9
            },
            {
                'name': 'Gynecology',
                'description': "Focuses on women's reproductive health",
                'keywords': ['menstrual problem', 'period pain', 'irregular period', 'pregnancy', 'infertility', 'uterine problem', 'ovarian cyst', 'pelvic pain', 'vaginal discharge', 'menopause', 'fibroids'],
                'sub_specialties': ['Obstetrics', 'Reproductive Endocrinology'],
                'priority': 8
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for specialty_data in specialties_data:
            specialty, created = MedicalSpecialty.objects.update_or_create(
                name=specialty_data['name'],
                defaults=specialty_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {specialty.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'⟳ Updated: {specialty.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nDone! Created {created_count}, Updated {updated_count}'))
