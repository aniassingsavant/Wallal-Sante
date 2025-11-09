from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone
import json

from .models import UserProfile, Notification, NotificationSettings, HealthEstablishment, AdminAuditLog
from .services import NotificationService

# === PAGES PUBLIQUES ===
def index(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            # Envoyer une notification de bienvenue si première connexion
            if not Notification.objects.filter(user=request.user).exists():
                NotificationService.send_news_alert(request.user, "Bienvenue sur Wallal Santé!")
        except UserProfile.DoesNotExist:
            pass
    
    return render(request, 'accueil/index.html')

def about(request):
    return render(request, 'accueil/about.html')

def actualites(request):
    # Redirection vers le site du ministère
    return redirect('https://www.minsante.cm/site/?q=fr/cat%C3%A9gories/actualit%C3%A9s')

# === INSCRIPTION ET CONNEXION ===
def register(request):
    if request.method == 'POST':
        # Création de l'utilisateur
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Création du profil avec toutes les données
        profile = UserProfile.objects.create(
            user=user,
            language=request.POST.get('language', 'fr'),
            first_name=request.POST.get('first_name', ''),
            age_group=request.POST.get('age_group'),
            gender=request.POST.get('gender'),
            is_pregnant=request.POST.get('is_pregnant', 'na'),
            chronic_diseases=request.POST.getlist('chronic_diseases'),
            other_disease=request.POST.get('other_disease', ''),
            has_allergies=request.POST.get('has_allergies') == 'true',
            allergies_details=request.POST.get('allergies_details', ''),
            regular_medication=request.POST.get('regular_medication') == 'true',
            medication_details=request.POST.get('medication_details', ''),
            health_access=request.POST.get('health_access', 'unknown'),
            allow_geolocation=request.POST.get('allow_geolocation') == 'true',
            recent_symptoms=request.POST.getlist('recent_symptoms'),
            audio_preference=request.POST.get('audio_preference') == 'true',
            data_consent=request.POST.get('data_consent') == 'true',
            phone=request.POST.get('phone', ''),
            region=request.POST.get('region'),
            village=request.POST.get('village', ''),
            outdoor_work=request.POST.get('outdoor_work') == 'true',
            no_mosquito_net=request.POST.get('no_mosquito_net') == 'true',
            stagnant_water=request.POST.get('stagnant_water') == 'true',
        )
        
        # Créer les paramètres de notifications par défaut
        NotificationSettings.objects.create(user=user)
        
        # Connecter l'utilisateur
        login(request, user)
        
        # Log d'audit
        AdminAuditLog.objects.create(
            user=user,
            action='CREATE',
            model_name='UserProfile',
            object_id=str(profile.id),
            details='Nouvel utilisateur inscrit'
        )
        
        return redirect('accueil')
    
    return render(request, 'accueil/register.html')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Log de connexion
            AdminAuditLog.objects.create(
                user=user,
                action='LOGIN',
                model_name='User',
                details='Connexion utilisateur'
            )
            
            return redirect('accueil')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accueil/login.html', {'form': form})

# === NOTIFICATIONS ===
@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'accueil/notifications.html', {'notifications': notifications})

@login_required
def notifications_api(request):
    notifications = Notification.objects.filter(user=request.user)[:10]
    profile = request.user.userprofile
    
    data = {
        'notifications': [
            {
                'id': n.id,
                'type': n.type,
                'title': n.title_ful if profile.language == 'ful' else n.title_fr,
                'message': n.message_ful if profile.language == 'ful' else n.message_fr,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%d/%m/%Y %H:%M')
            }
            for n in notifications
        ]
    }
    return JsonResponse(data)

@login_required
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

# === BACKOFFICE ===
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
        'establishments_count': HealthEstablishment.objects.count(),
    }
    
    # Graphique des inscriptions
    user_registrations = User.objects.filter(
        date_joined__gte=last_week
    ).extra({
        'date': "date(date_joined)"
    }).values('date').annotate(count=Count('id'))
    
    return render(request, 'accueil/backoffice_dashboard.html', {
        'stats': stats,
        'user_registrations': list(user_registrations)
    })

@user_passes_test(admin_required)
def manage_establishments(request):
    establishments = HealthEstablishment.objects.all()
    
    if request.method == 'POST':
        # Ajouter un établissement
        establishment = HealthEstablishment.objects.create(
            name=request.POST.get('name'),
            type=request.POST.get('type'),
            region=request.POST.get('region'),
            address=request.POST.get('address'),
            phone=request.POST.get('phone'),
        )
        
        AdminAuditLog.objects.create(
            user=request.user,
            action='CREATE',
            model_name='HealthEstablishment',
            object_id=str(establishment.id),
            details=f'Création établissement: {establishment.name}'
        )
        
        return redirect('manage_establishments')
    
    return render(request, 'accueil/manage_establishments.html', {
        'establishments': establishments
    })