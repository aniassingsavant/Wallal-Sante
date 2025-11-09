# api/models.py (ajouter ces modèles)
from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ('VACCINE', 'Rappel vaccin'),
        ('CAMPAIGN', 'Campagne santé'),
        ('WEATHER', 'Alerte météo'),
        ('EPIDEMIC', 'Alerte épidémie'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title_fulfulde = models.CharField(max_length=200)
    message_fulfulde = models.TextField()
    related_url = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class NotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='api_notification_settings')
    vaccine_reminders = models.BooleanField(default=True)
    campaign_alerts = models.BooleanField(default=True)
    weather_alerts = models.BooleanField(default=True)
    epidemic_alerts = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='07:00')