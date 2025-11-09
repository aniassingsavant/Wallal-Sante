# api/services.py (nouveau fichier)
from django.utils import timezone
from datetime import time
from .models import Notification, NotificationSettings

class NotificationService:
    @staticmethod
    def can_send_notification(user):
        try:
            settings = user.notificationsettings
            now = timezone.now().time()
            
            # Vérifier les heures respectueuses
            if settings.quiet_hours_start <= now <= settings.quiet_hours_end:
                return False
            return True
        except NotificationSettings.DoesNotExist:
            return True

    @staticmethod
    def send_vaccine_reminder(user, vaccine_name, due_date, detail_url=""):
        if NotificationService.can_send_notification(user):
            title = "💉 Tiiɗtol Vaccin"
            message = f"Tiiɗtol maa vaccin {vaccine_name} ngal fow no feewi. Ɗaɗol ngam ɓeydude humpito."
            
            Notification.objects.create(
                user=user,
                type='VACCINE',
                title_fulfulde=title,
                message_fulfulde=message,
                related_url=detail_url
            )

    @staticmethod
    def send_epidemic_alert(user, disease_name, region, alert_url=""):
        if NotificationService.can_send_notification(user):
            title = "🚨 Aade Nyaw"
            message = f"Aade {disease_name} no fowta e {region}. Tikkɗe heewde e {alert_url}"
            
            Notification.objects.create(
                user=user,
                type='EPIDEMIC',
                title_fulfulde=title,
                message_fulfulde=message,
                related_url=alert_url
            )