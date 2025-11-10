# accueil/services.py
from django.conf import settings

class NotificationService:
    @staticmethod
    def send_news_alert(user, message):
        """Envoie une notification d'actualité à l'utilisateur"""
        from .models import Notification
        
        # Créer la notification en français et fulfulde
        notification = Notification.objects.create(
            user=user,
            type='NEWS',
            title_fr="Bienvenue sur Wallal Santé!",
            title_ful="Ballital e Wallal Sante!",
            message_fr=message,
            message_ful="Ballital e Wallal Sante!",
            is_read=False
        )
        return notification

    @staticmethod
    def send_vaccine_reminder(user, vaccine_name, due_date):
        """Envoie un rappel de vaccin"""
        from .models import Notification
        
        notification = Notification.objects.create(
            user=user,
            type='VACCINE',
            title_fr=f"Rappel de vaccin: {vaccine_name}",
            title_ful=f"Faddu gootal: {vaccine_name}",
            message_fr=f"Votre vaccin {vaccine_name} est dû le {due_date}",
            message_ful=f"Gootal maa {vaccine_name} faddu hono {due_date}",
            is_read=False
        )
        return notification

class HealthService:
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calcule la distance entre deux points GPS (en km)"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Rayon de la Terre en km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

    @staticmethod
    def find_nearby_health_centers(user_lat, user_lon, max_distance_km=5):
        """Trouve les centres de santé dans un rayon de 5km"""
        from .models import HealthCenter
        
        nearby_centers = []
        all_centers = HealthCenter.objects.filter(is_active=True)
        
        for center in all_centers:
            distance = HealthService.calculate_distance(
                user_lat, user_lon, center.latitude, center.longitude
            )
            
            if distance <= max_distance_km:
                center_data = {
                    'id': center.id,
                    'name': center.name,
                    'type': center.type,
                    'village': center.village,
                    'address': center.address,
                    'phone': center.phone,
                    'distance_km': round(distance, 2),
                    'available_medications': center.available_medications,
                    'latitude': center.latitude,
                    'longitude': center.longitude,
                }
                nearby_centers.append(center_data)
        
        # Trier par distance
        return sorted(nearby_centers, key=lambda x: x['distance_km'])

class TranslationService:
    @staticmethod
    def translate_fulfulde_to_french(text):
        """Traduit du Fulfulde vers le Français"""
        # Pour le moment, retourne le texte tel quel
        return text

    @staticmethod
    def translate_french_to_fulfulde(text):
        """Traduit du Français vers le Fulfulde"""
        return text

# Alias pour la compatibilité
NotificationService = NotificationService