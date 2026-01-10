from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from .forms import DoctorRegistrationForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from .models import DoctorProfile


class FindDoctorView(View):
    def get(self, request):
        # 1. Fetch Approved Doctors
        doctors = DoctorProfile.objects.filter(is_approved=True).order_by('-id')
        
        # 2. Search Logic
        query = request.GET.get('q')
        if query:
            doctors = doctors.filter(
                Q(user__first_name__icontains=query) | 
                Q(user__last_name__icontains=query) |
                Q(specialization__icontains=query) |
                Q(sub_specialty__icontains=query) |
                Q(city__icontains=query)
            )

        # 3. Add Rating & Review Counts (Critical for your design)
        doctors = doctors.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )

        # 4. Pagination (6 doctors per page)
        paginator = Paginator(doctors, 6) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'query': query,
            'total_count': doctors.count(),
        }
        return render(request, 'find_doctor/find_doctor.html', context)
    



from django.shortcuts import render, get_object_or_404
from django.views import View
from django.db.models import Avg, Count
from .models import DoctorProfile, DoctorSchedule, DoctorReview
import json
from django.core.serializers.json import DjangoJSONEncoder

class DcotorDetailsView(View):
    def get(self, request, pk):
        # 1. Fetch Doctor
        doctor = get_object_or_404(DoctorProfile, pk=pk)
        
        # 2. Fetch Stats
        stats = doctor.reviews.aggregate(avg=Avg('rating'), count=Count('id'))
        avg_rating = stats['avg'] or 0
        review_count = stats['count'] or 0
        reviews = doctor.reviews.select_related('user').order_by('-created_at')

        # 3. FETCH & SERIALIZE SCHEDULE (The Magic Part)
        # We need to turn the database objects into a simple list for JavaScript
        schedules = DoctorSchedule.objects.filter(doctor=doctor)
        schedule_data = []
        for sch in schedules:
            schedule_data.append({
                'day': sch.day, # 'Mon', 'Tue'
                'start': sch.start_time.strftime("%H:%M"), # '09:00'
                'end': sch.end_time.strftime("%H:%M")     # '17:00'
            })

        context = {
            'doctor': doctor,
            'avg_rating': round(avg_rating, 1),
            'review_count': review_count,
            'reviews': reviews,
            # Pass the JSON string to the template
            'schedule_json': json.dumps(schedule_data, cls=DjangoJSONEncoder) 
        }
        return render(request, 'find_doctor/doctor_detail.html', context)

    def post(self, request, pk):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to review.")
            return redirect('login')
        
        doctor = get_object_or_404(DoctorProfile, pk=pk)
        
        # Check if already reviewed
        if DoctorReview.objects.filter(user=request.user, doctor=doctor).exists():
            messages.warning(request, "You have already reviewed this doctor.")
            return redirect('doctor_detail', pk=pk)
            
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating:
            DoctorReview.objects.create(
                user=request.user,
                doctor=doctor,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Review submitted successfully!")
        else:
            messages.error(request, "Please select a star rating.")
            
        return redirect('doctor_detail', pk=pk)

# find_doctor/views.py

class DoctorRegistrationView(View):
    template_name = 'find_doctor/doctor_registration.html'

    def get(self, request):
        form = DoctorRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # Ensure request.FILES is passed for file uploads
        form = DoctorRegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                form.save()
                return redirect('registration_success') 
            except Exception as e:
                print(f"--- SYSTEM ERROR: {e} ---") # Print system errors
                messages.error(request, f"System Error: {e}")
        else:
            # --- ADD THIS BLOCK TO SEE WHY IT FAILS ---
            print("\n" + "="*30)
            print("❌ FORM VALIDATION FAILED!")
            print(form.errors)  
            print("="*30 + "\n")
            # ------------------------------------------
            messages.error(request, "Registration failed. Check errors.")
            
        return render(request, self.template_name, {'form': form})


def check_email(request):
    email = request.GET.get('email', None)
    response = {
        'exists': False
    }
    if email:
        User = get_user_model()
        # Check if ANY user exists with this email
        if User.objects.filter(email__iexact=email).exists():
            response['exists'] = True
            
    return JsonResponse(response)

    
class RegistrationSuccessView(View):
    def get(self, request):
        return render(request, 'find_doctor/registration_success.html')