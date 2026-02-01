"""
Doctor Recommendation Engine
Matches patients with doctors based on symptoms, diseases, and conditions
"""

from django.db.models import Avg, Count
from .models import DoctorProfile, MedicalSpecialty
import re


class DoctorRecommendationEngine:
    """
    Intelligent recommendation engine that matches patient symptoms 
    to appropriate medical specialties and ranks doctors by according to their speciality, experiance, rating, fee and review count
    """
    
    def __init__(self):
        # Scoring weights - Option A: Balanced Approach
        # Total must sum to 1.0
        self.weights = {
            'rating': 0.25,         # 25% - Patient satisfaction & quality
            'experience': 0.20,     # 20% - Years of expertise
            'affordability': 0.15,  # 15% - Consultation fee (lower = better)
            'review_count': 0.05,   # 5% - Social proof
        }
        # Note: Specialty match (35%) is handled separately in ranking
        # Total: 25 + 20 + 15 + 5 = 65% (+ 35% specialty match = 100%)
    
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
        
        # Remove special characters but keep spaces, commas, and common medical terms
        text = re.sub(r'[^\w\s,\-]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def find_matching_specialties(self, symptoms_text):
        """
        Find medical specialties that match the patient's symptoms
        
        Args:
            symptoms_text: Patient's description of symptoms/condition
            
        Returns:
            List of tuples: [(specialty_name, relevance_score), ...]
            Sorted by relevance score (highest first)
        """
        normalized_text = self.normalize_input(symptoms_text)
        
        # Get all medical specialties from database
        specialties = MedicalSpecialty.objects.all()
        
        matches = []
        
        for specialty in specialties:
            relevance_score = 0
            matched_keywords = []
            
            # Check each keyword in the specialty
            for keyword in specialty.keywords:
                keyword_lower = keyword.lower().strip()
                
                # Exact match (e.g., user typed exactly "diabetes")
                if keyword_lower == normalized_text:
                    relevance_score += 10
                    matched_keywords.append(keyword)
                
                # Contains match (e.g., "chest pain" in "severe chest pain and breathing")
                elif keyword_lower in normalized_text or normalized_text in keyword_lower:
                    relevance_score += 5
                    matched_keywords.append(keyword)
                
                # Word-level match (e.g., "pain" matches with "chest pain")
                else:
                    keyword_words = set(keyword_lower.split())
                    input_words = set(normalized_text.split())
                    
                    overlap = keyword_words.intersection(input_words)
                    if overlap:
                        # Score based on percentage of words matched
                        match_ratio = len(overlap) / max(len(keyword_words), 1)
                        relevance_score += match_ratio * 3
                        if match_ratio > 0.5:  # More than half the words match
                            matched_keywords.append(keyword)
            
            if relevance_score > 0:
                # Multiply by specialty priority (important specialties rank higher)
                final_score = relevance_score * specialty.priority
                matches.append({
                    'name': specialty.name,
                    'score': final_score,
                    'matched_keywords': matched_keywords
                })
        
        # Sort by relevance score (highest first)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches
    
    def calculate_doctor_score(self, doctor, min_fee=None, max_fee=None):
        """
        Calculate composite recommendation score for a doctor
        
        Args:
            doctor: DoctorProfile instance (must have avg_rating and review_count annotated)
            min_fee: Minimum consultation fee in dataset (for normalization)
            max_fee: Maximum consultation fee in dataset (for normalization)
            
        Returns:
            Float score between 0-100
        """
        # Rating score (0-5 stars normalized to 0-100)
        rating = doctor.avg_rating or 0
        rating_score = (rating / 5.0) * 100
        
        # Experience score (0-40+ years normalized to 0-100)
        experience = doctor.years_of_experience or 0
        experience_score = min((experience / 40.0) * 100, 100)
        
        # Review count score (0-100+ reviews normalized to 0-100)
        review_count = doctor.review_count or 0
        review_score = min((review_count / 100.0) * 100, 100)
        
        # Affordability score (INVERSE: lower fee = higher score)
        # If min/max fees provided, normalize. Otherwise use default scoring
        if min_fee is not None and max_fee is not None and max_fee > min_fee:
            fee = doctor.consultation_fee or max_fee
            # Inverse normalization: lowest fee gets 100, highest gets 0
            affordability_score = 100 - ((fee - min_fee) / (max_fee - min_fee)) * 100
            affordability_score = max(0, min(100, affordability_score))  # Clamp 0-100
        else:
            # Fallback: Simple inverse calculation
            fee = doctor.consultation_fee or 1000
            # NPR 500 = 100 points, NPR 3000 = ~17 points
            affordability_score = max(0, 100 - (fee - 500) / 25)
        
        # Calculate weighted total score (0-100)
        # Note: This is the doctor-level score (65% of final score)
        # The other 35% comes from specialty match score
        total_score = (
            rating_score * self.weights['rating'] +
            experience_score * self.weights['experience'] +
            affordability_score * self.weights['affordability'] +
            review_score * self.weights['review_count']
        )
        
        return round(total_score, 2)
    
    def recommend_doctors(self, symptoms_text, limit=12, min_score=0):
        """
        Main recommendation function - returns ranked list of doctors
        
        Args:
            symptoms_text: Patient's symptoms/disease description
            limit: Maximum number of doctors to return
            min_score: Minimum recommendation score threshold (0-100)
            
        Returns:
            List of DoctorProfile objects with added attributes:
                - recommendation_score: Composite score (0-100)
                - matched_specialty: Which specialty matched
                - match_reason: Why this doctor was recommended
        """
        # Step 1: Find matching specialties
        specialty_matches = self.find_matching_specialties(symptoms_text)
        
        if not specialty_matches:
            # No specialty matched - return empty list
            # The view will handle name search as fallback
            return []
        
        # Step 2: Extract specialty names for filtering
        specialty_names = [match['name'] for match in specialty_matches]
        
        # Step 3: Query doctors by matched specializations
        doctors = DoctorProfile.objects.filter(
            is_approved=True,
            specialization__in=specialty_names
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).select_related('user', 'hospital_affiliation')
        
        # Calculate min/max fees for normalization (from filtered doctors)
        fees = [d.consultation_fee for d in doctors if d.consultation_fee]
        min_fee = min(fees) if fees else 500
        max_fee = max(fees) if fees else 3000
        
        # Step 4: Score and rank doctors
        doctor_list = []
        
        for doctor in doctors:
            # Calculate recommendation score with fee normalization
            score = self.calculate_doctor_score(doctor, min_fee, max_fee)
            
            if score >= min_score:
                # Add recommendation metadata
                doctor.recommendation_score = score
                doctor.matched_specialty = doctor.specialization
                
                # Find which specialty match this doctor belongs to
                for match in specialty_matches:
                    if match['name'] == doctor.specialization:
                        doctor.match_reason = f"Recommended for: {', '.join(match['matched_keywords'][:3])}"
                        doctor.specialty_match_score = match['score']
                        break
                
                doctor_list.append(doctor)
        
        # Step 5: Sort by recommendation score (highest first)
        doctor_list.sort(key=lambda d: (d.specialty_match_score, d.recommendation_score), reverse=True)
        
        return doctor_list[:limit]
    
    def _get_fallback_doctors(self, limit):
        """
        Fallback when no specialty matches - return top-rated general doctors
        
        Args:
            limit: Number of doctors to return
            
        Returns:
            List of top-rated DoctorProfile objects
        """
        doctors = DoctorProfile.objects.filter(
            is_approved=True
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-avg_rating', '-review_count')[:limit]
        
        doctor_list = list(doctors)
        
        # Calculate min/max fees for normalization
        fees = [d.consultation_fee for d in doctor_list if d.consultation_fee]
        min_fee = min(fees) if fees else 500
        max_fee = max(fees) if fees else 3000
        
        for doctor in doctor_list:
            doctor.recommendation_score = self.calculate_doctor_score(doctor, min_fee, max_fee)
            doctor.matched_specialty = doctor.specialization
            doctor.match_reason = "Top rated doctor"
            doctor.specialty_match_score = 0
        
        return doctor_list
    
    def is_symptom_search(self, query):
        """
        Determine if a search query is likely a symptom/disease search
        
        Args:
            query: User search string
            
        Returns:
            Boolean - True if appears to be symptom search
        """
        if not query:
            return False
        
        query_lower = query.lower().strip()
        
        # Check if it's likely a doctor name (contains "dr" or "doctor")
        if 'dr.' in query_lower or 'dr ' in query_lower or 'doctor' in query_lower:
            return False
        
        # Check if matches any known specialty exactly
        known_specialties = MedicalSpecialty.objects.filter(
            name__iexact=query
        ).exists()
        
        if known_specialties:
            return False
        
        # Otherwise, treat as potential symptom
        return True
