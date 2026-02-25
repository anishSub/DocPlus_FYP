"""
Hospital Recommendation Engine
Matches patients with hospitals based on symptoms, departments, and quality factors
"""

from django.db.models import Avg, Count
from .models import Hospital, Department
from datetime import datetime
import re


class HospitalRecommendationEngine:
    """
    Intelligent recommendation engine that matches patient symptoms 
    to appropriate hospital departments and ranks hospitals according to:
    - Department match (35%)
    - Patient rating (20%)
    - Location proximity (15%)
    - Hospital type (10%)
    - Services available (10%)
    """
    
    def __init__(self):
        # Scoring weights - Total must sum to 1.0
        self.weights = {
            'rating': 0.20,           # 20% - Patient satisfaction
            'location': 0.15,         # 15% - Geographic proximity
            'hospital_type': 0.10,    # 10% - Facility type relevance
            'services': 0.10,         # 10% - Available services/facilities
            'capacity': 0.03,         # 3% - Hospital size
            'experience': 0.03,       # 3% - Years established
            'review_count': 0.02,     # 2% - Social proof
            'emergency': 0.02,        # 2% - Emergency availability
        }
        # Note: Department match (35%) is handled separately in ranking
        # Total: 65% (+ 35% department match = 100%)
        
        # Department keyword mapping for symptom matching
        self.department_keywords = {
            'Cardiology': {
                'keywords': [
                    'heart', 'cardiac', 'chest pain', 'heart attack', 'angina',
                    'cardiovascular', 'coronary', 'arrhythmia', 'palpitation',
                    'heart failure', 'myocardial', 'blood pressure', 'hypertension'
                ],
                'priority': 1.0
            },
            'Orthopedics': {
                'keywords': [
                    'bone', 'fracture', 'joint', 'arthritis', 'knee', 'hip',
                    'back pain', 'spine', 'shoulder', 'ankle', 'wrist',
                    'osteoporosis', 'ligament', 'tendon', 'muscle pain'
                ],
                'priority': 1.0
            },
            'Neurology': {
                'keywords': [
                    'brain', 'nerve', 'seizure', 'epilepsy', 'stroke', 'paralysis',
                    'headache', 'migraine', 'parkinson', 'alzheimer', 'memory loss',
                    'numbness', 'tingling', 'tremor', 'neurological'
                ],
                'priority': 1.0
            },
            'Oncology': {
                'keywords': [
                    'cancer', 'tumor', 'chemotherapy', 'radiation', 'oncology',
                    'leukemia', 'lymphoma', 'carcinoma', 'malignant', 'biopsy',
                    'metastasis', 'oncologist'
                ],
                'priority': 1.2  # Higher priority for serious conditions
            },
            'Pediatrics': {
                'keywords': [
                    'child', 'children', 'baby', 'infant', 'pediatric', 'kid',
                    'newborn', 'vaccination', 'immunization', 'toddler', 'adolescent'
                ],
                'priority': 1.1
            },
            'Obstetrics and Gynecology': {
                'keywords': [
                    'pregnancy', 'pregnant', 'maternity', 'delivery', 'labor',
                    'gynecology', 'obstetrics', 'prenatal', 'postnatal', 'cesarean',
                    'miscarriage', 'menstrual', 'ovarian', 'uterine', 'breast'
                ],
                'priority': 1.1
            },
            'General Surgery': {
                'keywords': [
                    'surgery', 'operation', 'surgical', 'appendicitis', 'hernia',
                    'gallbladder', 'thyroid', 'trauma', 'emergency surgery'
                ],
                'priority': 1.0
            },
            'Internal Medicine': {
                'keywords': [
                    'diabetes', 'thyroid', 'kidney', 'liver', 'digestive',
                    'gastro', 'stomach', 'fever', 'infection', 'chronic disease',
                    'hypertension', 'cholesterol'
                ],
                'priority': 0.9
            },
            'Dermatology': {
                'keywords': [
                    'skin', 'rash', 'acne', 'eczema', 'psoriasis', 'allergy',
                    'dermatology', 'hair loss', 'skin cancer', 'mole'
                ],
                'priority': 0.8
            },
            'Ophthalmology': {
                'keywords': [
                    'eye', 'vision', 'cataract', 'glaucoma', 'retina', 'cornea',
                    'blind', 'eyesight', 'optical', 'lens'
                ],
                'priority': 0.9
            },
            'ENT': {
                'keywords': [
                    'ear', 'nose', 'throat', 'sinus', 'hearing', 'tonsil',
                    'voice', 'vertigo', 'dizziness', 'nasal'
                ],
                'priority': 0.9
            },
            'Pulmonology': {
                'keywords': [
                    'lung', 'respiratory', 'breathing', 'asthma', 'copd',
                    'pneumonia', 'tuberculosis', 'tb', 'cough', 'bronchitis'
                ],
                'priority': 1.0
            },
            'Nephrology': {
                'keywords': [
                    'kidney', 'renal', 'dialysis', 'urinary', 'kidney stone',
                    'nephrology', 'kidney failure'
                ],
                'priority': 1.0
            },
            'Psychiatry': {
                'keywords': [
                    'mental', 'depression', 'anxiety', 'psychiatric', 'psychologist',
                    'stress', 'bipolar', 'schizophrenia', 'therapy', 'counseling'
                ],
                'priority': 0.9
            },
            'Emergency': {
                'keywords': [
                    'emergency', 'urgent', 'accident', 'trauma', 'critical',
                    'severe', 'immediate', '911', 'ambulance'
                ],
                'priority': 1.3  # Highest priority for emergencies
            }
        }
    
    def normalize_input(self, text):
        """
        Clean and normalize user input for consistent matching
        
        Args:
            text: Raw user input string
            
        Returns:
            Normalized lowercase string without special characters
        """
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s,\-]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def find_matching_departments(self, symptoms_text):
        """
        Find hospital departments that match the patient's symptoms
        
        Args:
            symptoms_text: Patient's description of symptoms/condition
            
        Returns:
            List of dicts: [{'name': 'Cardiology', 'score': 50, 'matched_keywords': [...]}, ...]
            Sorted by relevance score (highest first)
        """
        normalized_text = self.normalize_input(symptoms_text)
        
        matches = []
        
        for dept_name, dept_data in self.department_keywords.items():
            relevance_score = 0
            matched_keywords = []
            
            # Check each keyword
            for keyword in dept_data['keywords']:
                keyword_lower = keyword.lower().strip()
                
                # Exact match
                if keyword_lower == normalized_text:
                    relevance_score += 10
                    matched_keywords.append(keyword)
                
                # Contains match
                elif keyword_lower in normalized_text or normalized_text in keyword_lower:
                    relevance_score += 5
                    matched_keywords.append(keyword)
                
                # Word-level match
                else:
                    keyword_words = set(keyword_lower.split())
                    input_words = set(normalized_text.split())
                    
                    overlap = keyword_words.intersection(input_words)
                    if overlap:
                        match_ratio = len(overlap) / max(len(keyword_words), 1)
                        relevance_score += match_ratio * 3
                        if match_ratio > 0.5:
                            matched_keywords.append(keyword)
            
            if relevance_score > 0:
                # Apply department priority
                final_score = relevance_score * dept_data['priority']
                matches.append({
                    'name': dept_name,
                    'score': final_score,
                    'matched_keywords': matched_keywords[:3]  # Top 3 matches
                })
        
        # Sort by score (highest first)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches
    
    def calculate_hospital_type_score(self, hospital_type, is_emergency=False, is_pediatric=False):
        """
        Score hospital type based on context
        
        Args:
            hospital_type: Type of hospital
            is_emergency: Whether this is an emergency search
            is_pediatric: Whether this is a pediatric search
            
        Returns:
            Score 0-100
        """
        scores = {
            'Super-Specialty': 100,
            'Multi-Specialty': 85,
            'Teaching': 75,
            'General': 60,
            'Children': 50,
        }
        
        base_score = scores.get(hospital_type, 50)
        
        # Boost children's hospitals for pediatric searches
        if is_pediatric and hospital_type == 'Children':
            base_score = 100
        
        return base_score
    
    def calculate_hospital_score(self, hospital, user_city=None, is_emergency=False, 
                                 is_pediatric=False, min_fee=None, max_fee=None):
        """
        Calculate composite recommendation score for a hospital
        
        Args:
            hospital: Hospital instance (must have avg_rating and review_count annotated)
            user_city: User's city for location matching
            is_emergency: Whether emergency search
            is_pediatric: Whether pediatric search
            
        Returns:
            Float score between 0-100
        """
        # Rating score (0-5 stars normalized to 0-100)
        rating = hospital.avg_rating or 0
        rating_score = (rating / 5.0) * 100
        
        # Location score
        if user_city and hospital.city:
            if hospital.city.lower().strip() == user_city.lower().strip():
                location_score = 100
            elif hospital.district and user_city.lower() in hospital.district.lower():
                location_score = 70
            else:
                location_score = 30
        else:
            location_score = 50  # Neutral if no location specified
        
        # Hospital type score
        hospital_type_score = self.calculate_hospital_type_score(
            hospital.hospital_type, is_emergency, is_pediatric
        )
        
        # Services score (based on number of services)
        service_count = hospital.services.count() if hasattr(hospital, 'services') else 0
        services_score = min((service_count / 10.0) * 100, 100)
        
        # Capacity score (number of beds)
        capacity = hospital.total_beds or 0
        capacity_score = min((capacity / 500.0) * 100, 100)
        
        # Experience score (years since establishment)
        if hospital.established_year:
            current_year = datetime.now().year
            years = current_year - hospital.established_year.year
            experience_score = min((years / 30.0) * 100, 100)
        else:
            experience_score = 50
        
        # Review count score
        review_count = hospital.review_count or 0
        review_score = min((review_count / 50.0) * 100, 100)
        
        # Emergency bonus
        emergency_score = 100 if hospital.emergency_available else 50
        
        # Calculate weighted total score (0-100)
        total_score = (
            rating_score * self.weights['rating'] +
            location_score * self.weights['location'] +
            hospital_type_score * self.weights['hospital_type'] +
            services_score * self.weights['services'] +
            capacity_score * self.weights['capacity'] +
            experience_score * self.weights['experience'] +
            review_score * self.weights['review_count'] +
            emergency_score * self.weights['emergency']
        )
        
        return round(total_score, 2)
    
    def recommend_hospitals(self, symptoms_text, city=None, limit=12, min_score=0):
        """
        Main recommendation function - returns ranked list of hospitals
        
        Args:
            symptoms_text: Patient's symptoms/condition description
            city: Optional city filter
            limit: Maximum number of hospitals to return
            min_score: Minimum recommendation score threshold (0-100)
            
        Returns:
            List of Hospital objects with added attributes:
                - recommendation_score: Composite score (0-100)
                - matched_departments: Which departments matched
                - match_reason: Why this hospital was recommended
        """
        # Step 1: Find matching departments
        department_matches = self.find_matching_departments(symptoms_text)
        
        if not department_matches:
            # No department matched - return empty list
            return []
        
        # Check for special contexts
        is_emergency = 'emergency' in symptoms_text.lower() or 'urgent' in symptoms_text.lower()
        is_pediatric = any(kw in symptoms_text.lower() for kw in ['child', 'children', 'baby', 'kid', 'infant'])
        
        # Step 2: Extract department names for filtering
        department_names = [match['name'] for match in department_matches]
        
        # Step 3: Query hospitals by matched departments
        hospitals = Hospital.objects.filter(
            is_verified=True,
            departments__name__in=department_names
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).select_related('user').prefetch_related('services', 'departments').distinct()
        
        # Apply city filter if provided
        if city:
            hospitals = hospitals.filter(city__iexact=city)
        
        # Step 4: Score and rank hospitals
        hospital_list = []
        
        for hospital in hospitals:
            # Calculate hospital score
            score = self.calculate_hospital_score(
                hospital, 
                user_city=city, 
                is_emergency=is_emergency,
                is_pediatric=is_pediatric
            )
            
            if score >= min_score:
                # Find which departments matched
                matched_depts = []
                dept_match_score = 0
                
                for match in department_matches:
                    if hospital.departments.filter(name=match['name']).exists():
                        matched_depts.append(match['name'])
                        dept_match_score = max(dept_match_score, match['score'])
                
                # Add recommendation metadata
                hospital.recommendation_score = score
                hospital.matched_departments = matched_depts
                hospital.department_match_score = dept_match_score
                
                # Create match reason
                if matched_depts:
                    dept_str = ', '.join(matched_depts[:2])
                    hospital.match_reason = f"Has {dept_str}"
                else:
                    hospital.match_reason = "Recommended hospital"
                
                hospital_list.append(hospital)
        
        # Step 5: Sort by department match score, then hospital score
        hospital_list.sort(
            key=lambda h: (h.department_match_score, h.recommendation_score), 
            reverse=True
        )
        
        return hospital_list[:limit]
    
    def is_symptom_search(self, query):
        """
        Determine if a search query is likely a symptom/condition search
        
        Args:
            query: User search string
            
        Returns:
            Boolean - True if appears to be symptom search
        """
        if not query:
            return False
        
        query_lower = query.lower().strip()
        
        # Check if matches any department keywords
        for dept_data in self.department_keywords.values():
            for keyword in dept_data['keywords']:
                if keyword.lower() in query_lower:
                    return True
        
        return False
