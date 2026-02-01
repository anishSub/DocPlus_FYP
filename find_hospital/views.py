from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction 
from .models import Hospital, Service, Department 
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.db.models import Q, Avg, Count

class FindHospitalView(View):
    def get(self, request):
        # Get search query from URL (e.g., ?q=heart attack)
        query = request.GET.get('q', '').strip()
        city_filter = request.GET.get('city', '').strip()
        
        hospitals = []
        search_type = 'browse'  # Default
        total_count = 0
        
        if query:
            # Import recommendation engine
            from .services import HospitalRecommendationEngine
            
            # Initialize recommendation engine
            engine = HospitalRecommendationEngine()
            
            # Check if it's a symptom/condition search
            if engine.is_symptom_search(query):
                # Use recommendation engine
                search_type = 'recommendation'
                hospitals = engine.recommend_hospitals(
                    symptoms_text=query,
                    city=city_filter if city_filter else None,
                    limit=20
                )
                total_count = len(hospitals)
            else:
                # Fallback: Name/location search
                search_type = 'name_search'
                hospitals = Hospital.objects.filter(
                    is_verified=True
                ).filter(
                    Q(name__icontains=query) |
                    Q(city__icontains=query) |
                    Q(district__icontains=query)
                ).annotate(
                    avg_rating=Avg('reviews__rating'),
                    review_count=Count('reviews')
                ).order_by('-avg_rating', 'name')
                
                if city_filter:
                    hospitals = hospitals.filter(city__iexact=city_filter)
                
                total_count = hospitals.count()
        else:
            # No query - show all verified hospitals
            hospitals = Hospital.objects.filter(
                is_verified=True
            ).annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            ).order_by('-avg_rating', 'name')
            
            if city_filter:
                hospitals = hospitals.filter(city__iexact=city_filter)
            
            total_count = hospitals.count()

        # Get unique cities for filter dropdown
        cities = Hospital.objects.filter(
            is_verified=True
        ).values_list('city', flat=True).distinct().order_by('city')

        context = {
            'hospitals': hospitals,
            'total_count': total_count,
            'query': query,
            'city_filter': city_filter,
            'cities': cities,
            'search_type': search_type,
        }
        return render(request, 'find_hospital/find_hospital.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import F, Avg, Count
from .models import Hospital, HospitalReview
from find_doctor.models import DoctorProfile

# ... other views ...

class HospitalDetailView(View):
    def get(self, request, pk):
        # 1. Fetch Hospital
        hospital = get_object_or_404(Hospital, pk=pk)
        
        # 2. Increment View Counter
        Hospital.objects.filter(pk=pk).update(total_views=F('total_views') + 1)
        hospital.refresh_from_db()
        
        # 3. Get Statistics
        # Count approved doctors linked to this hospital
        doctor_count = DoctorProfile.objects.filter(
            hospital_affiliation=hospital, 
            is_approved=True
        ).count()
        
        # Get Reviews & Ratings
        reviews = HospitalReview.objects.filter(hospital=hospital).order_by('-created_at')
        review_count = reviews.count()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        avg_rating = round(avg_rating, 1) if avg_rating else 0.0

        context = {
            'hospital': hospital,
            'doctor_count': doctor_count,
            'reviews': reviews,
            'review_count': review_count,
            'avg_rating': avg_rating,
        }
        return render(request, 'find_hospital/hospital_detail.html', context)
    

User = get_user_model()


class HospitalRegistrationView(View):
    def get(self, request):
        return render(request, 'find_hospital/hospital_registration.html')

    def post(self, request):
        try:
            # Use atomic transaction: If hospital fails, User is not created.
            with transaction.atomic():
                data = request.POST
                files = request.FILES
                
                # --- 1. Password Validation ---
                password = data.get('password')
                password_confirm = data.get('password_confirm')
                email = data.get('email')

                if password != password_confirm:
                    messages.error(request, "Passwords do not match.")
                    return render(request, 'find_hospital/hospital_registration.html')

                if User.objects.filter(email=email).exists():
                    messages.error(request, "Email already registered.")
                    return render(request, 'find_hospital/hospital_registration.html')

                # --- 2. Create the User Account ---
                user = User.objects.create_user(
                    username=email, 
                    email=email, 
                    password=password,
                    role='HOSPITAL_ADMIN' # Use string if your model expects a charfield
                )

                # --- 3. Create Hospital (WITHOUT M2M Fields) 
                hospital = Hospital.objects.create(
                    user=user,
                    name=data.get('name'),
                    hospital_type=data.get('hospital_type'),
                    established_year=data.get('established_year'),
                    phone=data.get('phone'),
                    email=email,
                    city=data.get('city'),
                    district=data.get('district'),
                    website=data.get('website'),
                    appointment_link=data.get('appointment_link'),
                    address=data.get('address'),
                    
                    total_beds=data.get('total_beds'),
                    # total_doctors=data.get('total_doctors'), # <--- REMOVED (Not in Model)
                    description=data.get('description'),
                    
                    image=files.get('image'),
                    
                    # Handle Checkbox: 'on' means True, None means False
                    emergency_available=True if data.get('emergency_available') == 'on' else False,
                    
                    opd_start=data.get('opd_start'),
                    opd_end=data.get('opd_end'),
                    achievements=data.get('achievements')
                )

                # --- 4. Handle Services (Many-to-Many) ---
                # Get the list of strings checked by user: ['ICU', 'Lab']
                services_list = request.POST.getlist('services') 
                
                for s_name in services_list:
                    # Get the Service OBJECT from DB, or create it if missing
                    service_obj, _ = Service.objects.get_or_create(name=s_name)
                    # Link it to the hospital
                    hospital.services.add(service_obj)

                # --- 5. Handle Departments (Many-to-Many) ---
                # Get string: "Dental, Ortho" -> Split into List: ['Dental', 'Ortho']
                dept_str = data.get('departments', '')
                if dept_str:
                    dept_names = [d.strip() for d in dept_str.split(',') if d.strip()]
                    
                    for d_name in dept_names:
                        # Get the Department OBJECT from DB
                        dept_obj, _ = Department.objects.get_or_create(name=d_name)
                        # Link it
                        hospital.departments.add(dept_obj)

                messages.success(request, "Registration Submitted Successfully!")
                return redirect('hospital_success')

        except Exception as e:
            print("Error Saving Hospital:", e)
            messages.error(request, f"Something went wrong: {e}")
            return render(request, 'find_hospital/hospital_registration.html')




# 1. Update Detail View to Count Page Visits
class HospitalDetailView(View):
    def get(self, request, pk):
        hospital = get_object_or_404(Hospital, pk=pk)
        
        # Increment View Counter (F expression avoids race conditions)
        Hospital.objects.filter(pk=pk).update(total_views=F('total_views') + 1)
        
        # Refresh to get new value
        hospital.refresh_from_db()
        
        context = {'hospital': hospital}
        return render(request, 'find_hospital/hospital_detail.html', context)



def track_website_click(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    link_type = request.GET.get('type') # Get the '?type=' parameter from URL
    
    target_url = None

    if link_type == 'appointment' and hospital.appointment_link:
        # Increment a specific counter if you want, or just the general one
        Hospital.objects.filter(pk=pk).update(total_website_clicks=F('total_website_clicks') + 1)
        target_url = hospital.appointment_link

    elif link_type == 'website' and hospital.website:
        # You could count 'total_views' here or 'clicks' depending on your preference
        Hospital.objects.filter(pk=pk).update(total_website_clicks=F('total_website_clicks') + 1)
        target_url = hospital.website
    
    # Fallback if something is wrong
    if not target_url:
        return redirect('hospital_detail', pk=pk)

    # Ensure http:// prefix
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'http://' + target_url
        
    return redirect(target_url)
    
    
    
class Hospital_successView(View):
    def get(self,request):
        return render(request, 'find_hospital/registration_success.html')