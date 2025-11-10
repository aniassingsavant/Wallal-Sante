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

from .services import HealthService, TranslationService, NotificationService
import json
import json

def process_voice_query(request):
    """Traitement des requêtes vocales Fulfulde"""
    if request.method == 'POST':
        try:
            from .services import TranslationService, HealthService
            
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            
            # Récupérer les données
            fulfulde_text = request.POST.get('fulfulde_text')
            user_lat = request.POST.get('latitude')
            user_lon = request.POST.get('longitude')
            
            if not fulfulde_text:
                return JsonResponse({'error': 'Texte Fulfulde manquant'}, status=400)
            
            # Traduction Fulfulde → Français
            french_translation = TranslationService.translate_fulfulde_to_french(fulfulde_text)
            
            # Appel au chatbot (à intégrer avec l'API de ton collègue)
            chatbot_response_fr = call_chatbot_api(french_translation, user_profile.to_json())
            
            # Centres de santé proches
            nearby_centers = []
            if user_lat and user_lon:
                nearby_centers = HealthService.find_nearby_health_centers(
                    float(user_lat), float(user_lon)
                )
            
            # Traduction réponse → Fulfulde
            chatbot_response_ful = TranslationService.translate_french_to_fulfulde(chatbot_response_fr)
            
            return JsonResponse({
                'success': True,
                'response_fulfulde': chatbot_response_ful,
                'health_centers': nearby_centers,
                'translation': french_translation
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def call_chatbot_api(user_message, user_profile):
    """Simulation d'appel au chatbot"""
    # À remplacer par l'appel réel à l'API de ton collègue
    return f"Réponse basée sur votre profil: {user_profile.get('age_group', 'N/A')}"

# Ajoute cette fonction à la fin de ton views.py
def get_health_centers(request):
    """API pour récupérer les centres de santé"""
    try:
        from .models import HealthCenter
        
        # Récupérer les paramètres de filtre
        region = request.GET.get('region', '')
        max_distance = request.GET.get('max_distance', 50)  # km par défaut
        
        centers = HealthCenter.objects.filter(is_active=True)
        
        if region:
            centers = centers.filter(region__icontains=region)
        
        # Formater la réponse
        centers_data = []
        for center in centers:
            centers_data.append({
                'id': center.id,
                'name': center.name,
                'type': center.type,
                'region': center.region,
                'village': center.village,
                'address': center.address,
                'phone': center.phone,
                'latitude': center.latitude,
                'longitude': center.longitude,
                'available_medications': center.available_medications,
                'operating_hours': center.operating_hours,
            })
        
        return JsonResponse({
            'success': True,
            'centers': centers_data,
            'count': len(centers_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
def process_voice_query(request):
    if request.method == 'POST':
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            
            # Récupérer la requête voice Fulfulde
            fulfulde_text = request.POST.get('fulfulde_text')
            user_lat = request.POST.get('latitude')
            user_lon = request.POST.get('longitude')
            
            if not fulfulde_text:
                return JsonResponse({'error': 'Texte Fulfulde manquant'}, status=400)
            
            # 1. Traduction Fulfulde → Français
            french_translation = TranslationService.translate_fulfulde_to_french(fulfulde_text)
            
            # 2. Envoi au Chatbot (à intégrer avec l'API de ton collègue)
            chatbot_response_fr = call_chatbot_api(french_translation, user_profile.to_json())
            
            # 3. Trouver centres de santé proches
            nearby_centers = []
            if user_lat and user_lon:
                nearby_centers = HealthService.find_nearby_health_centers(
                    float(user_lat), float(user_lon)
                )
            
            # 4. Recommandations de médicaments
            medications = HealthService.get_recommended_medications(
                chatbot_response_fr, user_profile
            )
            
            # 5. Traduction réponse → Fulfulde
            chatbot_response_ful = TranslationService.translate_french_to_fulfulde(chatbot_response_fr)
            
            # 6. Sauvegarder la requête
            voice_query = VoiceQuery.objects.create(
                user=user,
                fulfulde_text=fulfulde_text,
                french_translation=french_translation,
                chatbot_response_fr=chatbot_response_fr,
                chatbot_response_ful=chatbot_response_ful,
                health_centers=nearby_centers,
                medications=medications,
            )
            
            # 7. Préparer réponse finale
            response_data = {
                'success': True,
                'response_fulfulde': chatbot_response_ful,
                'health_centers': nearby_centers,
                'recommended_medications': medications,
                'query_id': voice_query.id,
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def call_chatbot_api(user_message, user_profile):
    """Appelle l'API du chatbot développé par ton collègue"""
    try:
        # À adapter avec l'URL réelle de l'API du chatbot
        payload = {
            'message': user_message,
            'user_profile': user_profile,
            'language': 'fr'
        }
        
        # response = requests.post('http://localhost:8001/api/chatbot/', json=payload)
        # return response.json()['response']
        
        # Simulation en attendant l'intégration réelle
        return f"Réponse du chatbot basée sur votre profil: {user_profile}"
        
    except Exception as e:
        return f"Je vous recommande de consulter un centre de santé. Détails: {str(e)}"
from .models import UserProfile, Notification, NotificationSettings, HealthEstablishment, AdminAuditLog
from .services import NotificationService

# === PAGES PUBLIQUES ===
def index(request):
    try:
        return render(request, 'accueil/accueil.html')
    except Exception as e:
        from django.http import HttpResponse
        return HttpResponse(f"Erreur avec le template: {str(e)}")

def about(request):
    return render(request, 'accueil/a_propos.html')

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