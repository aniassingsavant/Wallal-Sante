# accueil/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Langue préférée
    LANGUAGE_CHOICES = [('fr', 'Français'), ('ful', 'Fulfulde')]
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='fr')
    
    # Prénom (optionnel)
    first_name = models.CharField(max_length=100, blank=True)
    
    # Âge
    AGE_GROUPS = [
        ('0-4', '0–4 ans'), ('5-14', '5–14 ans'), ('15-24', '15–24 ans'),
        ('25-44', '25–44 ans'), ('45-64', '45–64 ans'), ('65+', '65 ans et plus'),
    ]
    age_group = models.CharField(max_length=10, choices=AGE_GROUPS)
    
    # Sexe
    GENDER_CHOICES = [
        ('M', 'Homme'), ('F', 'Femme'), ('O', 'Autre'), ('N', 'Préfère pas dire'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Grossesse
    PREGNANCY_CHOICES = [('yes', 'Oui'), ('no', 'Non'), ('na', 'Ne s\'applique pas')]
    is_pregnant = models.CharField(max_length=3, choices=PREGNANCY_CHOICES, default='na')
    
    # Autres champs de base
    region = models.CharField(max_length=100)
    village = models.CharField(max_length=100, blank=True)
    data_consent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

# === NOTIFICATIONS ===
class Notification(models.Model):
    TYPE_CHOICES = [
        ('VACCINE', 'Rappel vaccin'),
        ('CAMPAIGN', 'Campagne santé'), 
        ('WEATHER', 'Alerte météo'),
        ('EPIDEMIC', 'Alerte épidémie'),
        ('NEWS', 'Actualité santé'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accueil_notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title_fr = models.CharField(max_length=200)
    title_ful = models.CharField(max_length=200)
    message_fr = models.TextField()
    message_ful = models.TextField()
    related_url = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class NotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accueil_notification_settings')
    vaccine_reminders = models.BooleanField(default=True)
    campaign_alerts = models.BooleanField(default=True)
    weather_alerts = models.BooleanField(default=True)
    epidemic_alerts = models.BooleanField(default=True)
    news_notifications = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='07:00')

# === BACKOFFICE ===
class HealthEstablishment(models.Model):
    TYPE_CHOICES = [
        ('HOSPITAL', 'Hôpital'),
        ('CLINIC', 'Clinique'), 
        ('DISPENSARY', 'Dispensaire'),
    ]
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    region = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.region}"

class AdminAuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Création'), ('UPDATE', 'Modification'), 
        ('DELETE', 'Suppression'), ('LOGIN', 'Connexion'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='accueil_audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)