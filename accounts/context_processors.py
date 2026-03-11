from .models import Institute

def institute_details(request):
    institute = Institute.objects.first()
    return {
        'institute': institute
    }