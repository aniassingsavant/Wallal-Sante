from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone
from accueil.models import UserProfile
from api.models import Notification

#creons les vues pour chaque page

def admin_required(user):
    return user.is_staff or user.is_superuser

def conseils(request):  
    return render(request, 'conseils/conseils.html')

def about(request):
    return render(request, 'conseils/about.html')

def register(request):
    return render(request, 'conseils/register.html')

def admin_required(user):
    return user.is_staff or user.is_superuser

@user_passes_test(admin_required)
def backoffice_dashboard(request):
    # Statistiques
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    
    stats = {
        'total_users': User.objects.count(),
        'profiles_completed': UserProfile.objects.count(),
        'fulfulde_users': UserProfile.objects.filter(language='ful').count(),
        'notifications_sent': Notification.objects.count(),
        'new_users_week': User.objects.filter(date_joined__gte=last_week).count(),
    }
    
    return render(request, 'conseils/backoffice_dashboard.html', {'stats': stats})

@user_passes_test(admin_required)
def manage_establishments(request):
    establishments = HealthEstablishment.objects.all()
    return render(request, 'conseils/manage_establishments.html', 
                 {'establishments': establishments})