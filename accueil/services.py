from django.utils import timezone
from datetime import time
from .models import Notification, NotificationSettings, UserProfile

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
    def send_vaccine_reminder(user, vaccine_name, due_date):
        if NotificationService.can_send_notification(user):
            profile = user.userprofile
            
            # Message selon la langue
            if profile.language == 'ful':
                title = "💉 Tiiɗtol Vaccin"
                message = f"Tiiɗtol maa vaccin {vaccine_name} ngal fow no feewi."
            else:
                title = "💉 Rappel de vaccin"
                message = f"Rappel pour le vaccin {vaccine_name} le {due_date}."
            
            Notification.objects.create(
                user=user,
                type='VACCINE',
                title_fr=f"Rappel vaccin {vaccine_name}",
                title_ful=f"Tiiɗtol Vaccin {vaccine_name}",
                message_fr=message,
                message_ful=message,
            )

    @staticmethod
    def send_epidemic_alert(user, disease_name, region):
        if NotificationService.can_send_notification(user):
            profile = user.userprofile
            
            if profile.language == 'ful':
                title = "🚨 Aade Nyaw"
                message = f"Aade {disease_name} no fowta e {region}. Tikkɗe heewde!"
            else:
                title = "🚨 Alerte épidémie"
                message = f"Alerte {disease_name} dans la région {region}. Prenez vos précautions!"
            
            Notification.objects.create(
                user=user,
                type='EPIDEMIC',
                title_fr=title,
                title_ful=title,
                message_fr=message,
                message_ful=message,
            )

    @staticmethod
    def send_news_alert(user, news_title):
        if NotificationService.can_send_notification(user):
            profile = user.userprofile
            
            if profile.language == 'ful':
                title = "📰 Humpito Hesere"
                message = f"Humpito hesere: {news_title}"
            else:
                title = "📰 Nouvelle actualité"
                message = f"Nouvelle actualité: {news_title}"
            
            Notification.objects.create(
                user=user,
                type='NEWS',
                title_fr=title,
                title_ful=title,
                message_fr=message,
                message_ful=message,
            )