from django.shortcuts import render

# Create your views here.
class HospitalAdminOverview:
    def overview(request):
        return render(request, 'hospitalAdmin/overview.html')