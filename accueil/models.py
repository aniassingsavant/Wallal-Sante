# accueil/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # 1. Langue préférée
    LANGUAGE_CHOICES = [('fr', 'Français'), ('ful', 'Fulfulde')]
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='fr')
    
    # 2. Prénom (optionnel)
    first_name = models.CharField(max_length=100, blank=True)
    
    # 3. Âge
    AGE_GROUPS = [
        ('0-4', '0–4 ans'), ('5-14', '5–14 ans'), ('15-24', '15–24 ans'),
        ('25-44', '25–44 ans'), ('45-64', '45–64 ans'), ('65+', '65 ans et plus'),
    ]
    age_group = models.CharField(max_length=10, choices=AGE_GROUPS)
    
    # 4. Sexe
    GENDER_CHOICES = [
        ('M', 'Homme'), ('F', 'Femme'), ('O', 'Autre'), ('N', 'Préfère pas dire'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # 5. Grossesse
    PREGNANCY_CHOICES = [('yes', 'Oui'), ('no', 'Non'), ('na', 'Ne s\'applique pas')]
    is_pregnant = models.CharField(max_length=3, choices=PREGNANCY_CHOICES, default='na')
    
    # 6. Maladies chroniques ou récurrentes
    DISEASE_CHOICES = [
        ('malaria', 'Paludisme (récurrent)'),
        ('diabetes', 'Diabète'),
        ('hypertension', 'Hypertension'), 
        ('asthma', 'Asthme'),
        ('hiv', 'VIH'),
        ('none', 'Aucune'),
        ('other', 'Autre'),
    ]
    chronic_diseases = models.JSONField(default=list)
    
    # Maladie autre (si "Autre" est sélectionné)
    other_disease = models.CharField(max_length=200, blank=True)
    
    # 7. Allergies
    has_allergies = models.BooleanField(default=False)
    allergies_details = models.TextField(blank=True)
    
    # 8. Médicaments réguliers
    regular_medication = models.BooleanField(default=False)
    medication_details = models.TextField(blank=True)
    
    # 9. Profession
    profession = models.CharField(max_length=100, blank=True)
    
    # 10. Statut vaccinal
    VACCINATION_CHOICES = [
        ('up_to_date', 'À jour'),
        ('partial', 'Partiel'), 
        ('none', 'Aucun'),
        ('unknown', 'Inconnu'),
    ]
    vaccination_status = models.CharField(max_length=20, choices=VACCINATION_CHOICES, default='unknown')
    
    # 11. Accès technologique
    internet_access = models.BooleanField(default=False)
    gsm_access = models.BooleanField(default=True)
    
    # 12. Localisation
    region = models.CharField(max_length=100)
    village = models.CharField(max_length=100, blank=True)
    
    # 13. Facteurs de risque environnementaux
    outdoor_work = models.BooleanField(default=False)
    no_mosquito_net = models.BooleanField(default=False)
    stagnant_water = models.BooleanField(default=False)
    
    # 14. Préférences utilisateur
    audio_preference = models.BooleanField(default=False)
    allow_geolocation = models.BooleanField(default=False)
    
    # 15. Consentement
    data_consent = models.BooleanField(default=False)
    
    # 16. Autres informations de santé
    recent_symptoms = models.JSONField(default=list, blank=True)
    health_access = models.CharField(max_length=20, default='unknown', choices=[
        ('good', 'Bon accès'),
        ('limited', 'Accès limité'),
        ('poor', 'Mauvais accès'),
        ('unknown', 'Inconnu')
    ])
    
    # Téléphone pour notifications
    phone = models.CharField(max_length=20, blank=True)
    
    # Géolocalisation
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

    def to_json(self):
        """Convertit le profil en JSON pour le chatbot"""
        return {
            'language': self.language,
            'first_name': self.first_name,
            'age_group': self.age_group,
            'gender': self.gender,
            'is_pregnant': self.is_pregnant,
            'chronic_diseases': self.chronic_diseases,
            'other_disease': self.other_disease,
            'has_allergies': self.has_allergies,
            'allergies_details': self.allergies_details,
            'regular_medication': self.regular_medication,
            'medication_details': self.medication_details,
            'profession': self.profession,
            'vaccination_status': self.vaccination_status,
            'internet_access': self.internet_access,
            'gsm_access': self.gsm_access,
            'region': self.region,
            'village': self.village,
            'outdoor_work': self.outdoor_work,
            'no_mosquito_net': self.no_mosquito_net,
            'stagnant_water': self.stagnant_water,
            'recent_symptoms': self.recent_symptoms,
            'health_access': self.health_access,
            'current_latitude': self.current_latitude,
            'current_longitude': self.current_longitude,
        }

    def get_health_risks(self):
        """Retourne les risques santé basés sur le profil"""
        risks = []
        if 'malaria' in self.chronic_diseases:
            risks.append('Paludisme récurrent')
        if self.outdoor_work:
            risks.append('Travail en extérieur (risque paludisme)')
        if self.no_mosquito_net:
            risks.append('Pas de moustiquaire')
        if self.stagnant_water:
            risks.append('Eau stagnante à proximité')
        return risks

# === VOICE QUERY & CHATBOT INTEGRATION ===
class VoiceQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voice_queries')
    fulfulde_audio = models.FileField(upload_to='voice_queries/', blank=True, null=True)
    fulfulde_text = models.TextField(help_text="Transcription Fulfulde de la requête vocale")
    french_translation = models.TextField(help_text="Traduction française de la requête")
    chatbot_response_fr = models.TextField(help_text="Réponse du chatbot en français")
    chatbot_response_ful = models.TextField(help_text="Réponse traduite en Fulfulde")
    health_centers = models.JSONField(default=list, help_text="Centres de santé à proximité")
    medications = models.JSONField(default=list, help_text="Médicaments recommandés")
    user_latitude = models.FloatField(null=True, blank=True)
    user_longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Requête vocale"
        verbose_name_plural = "Requêtes vocales"

    def __str__(self):
        return f"Requête de {self.user.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

# === HEALTH CENTERS & MEDICATIONS ===
class HealthCenter(models.Model):
    TYPE_CHOICES = [
        ('HOSPITAL', 'Hôpital'),
        ('CLINIC', 'Clinique'),
        ('PHARMACY', 'Pharmacie'),
        ('DISPENSARY', 'Dispensaire'),
        ('HEALTH_CENTER', 'Centre de santé'),
    ]
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    region = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    latitude = models.FloatField(help_text="Coordonnée GPS - latitude")
    longitude = models.FloatField(help_text="Coordonnée GPS - longitude")
    address = models.TextField()
    phone = models.CharField(max_length=20)
    available_medications = models.JSONField(
        default=list, 
        help_text="Liste des médicaments disponibles (noms ou IDs)"
    )
    operating_hours = models.CharField(max_length=100, default="08:00-18:00")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Centre de santé"
        verbose_name_plural = "Centres de santé"

    def __str__(self):
        return f"{self.name} - {self.village} ({self.region})"

class Medication(models.Model):
    TYPE_CHOICES = [
        ('ANTIMALARIAL', 'Antipaludique'),
        ('ANTIBIOTIC', 'Antibiotique'),
        ('ANALGESIC', 'Antidouleur'),
        ('ANTIPYRETIC', 'Antifièvre'),
        ('ANTIHISTAMINE', 'Antihistaminique'),
        ('VITAMIN', 'Vitamine'),
        ('OTHER', 'Autre'),
    ]
    
    name = models.CharField(max_length=200, help_text="Nom commercial du médicament")
    generic_name = models.CharField(max_length=200, help_text="Nom générique")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    prescription_required = models.BooleanField(default=False)
    common_uses = models.TextField(help_text="Indications courantes")
    dosage_forms = models.JSONField(
        default=list,
        help_text="Formes disponibles (comprimés, sirop, etc.)"
    )
    side_effects = models.TextField(blank=True, help_text="Effets secondaires courants")
    contraindications = models.TextField(blank=True, help_text="Contre-indications")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Médicament"
        verbose_name_plural = "Médicaments"

    def __str__(self):
        return f"{self.name} ({self.generic_name})"

# === NOTIFICATIONS ===
class Notification(models.Model):
    TYPE_CHOICES = [
        ('VACCINE', 'Rappel vaccin'),
        ('CAMPAIGN', 'Campagne santé'), 
        ('WEATHER', 'Alerte météo'),
        ('EPIDEMIC', 'Alerte épidémie'),
        ('NEWS', 'Actualité santé'),
        ('MEDICATION', 'Rappel médicament'),
        ('APPOINTMENT', 'Rappel rendez-vous'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accueil_notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title_fr = models.CharField(max_length=200)
    title_ful = models.CharField(max_length=200)
    message_fr = models.TextField()
    message_ful = models.TextField()
    related_url = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    scheduled_for = models.DateTimeField(null=True, blank=True, help_text="Planification de l'envoi")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.type} - {self.user.username}"

class NotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accueil_notification_settings')
    vaccine_reminders = models.BooleanField(default=True)
    campaign_alerts = models.BooleanField(default=True)
    weather_alerts = models.BooleanField(default=True)
    epidemic_alerts = models.BooleanField(default=True)
    news_notifications = models.BooleanField(default=True)
    medication_reminders = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='07:00')
    language_preference = models.CharField(
        max_length=10, 
        choices=[('fr', 'Français'), ('ful', 'Fulfulde')],
        default='fr'
    )
    
    class Meta:
        verbose_name = "Paramètre de notification"
        verbose_name_plural = "Paramètres de notification"

    def __str__(self):
        return f"Paramètres de {self.user.username}"

# === BACKOFFICE ===
class HealthEstablishment(models.Model):
    TYPE_CHOICES = [
        ('HOSPITAL', 'Hôpital'),
        ('CLINIC', 'Clinique'), 
        ('DISPENSARY', 'Dispensaire'),
        ('LABORATORY', 'Laboratoire'),
    ]
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    region = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Établissement de santé"
        verbose_name_plural = "Établissements de santé"

    def __str__(self):
        return f"{self.name} - {self.region}"

class AdminAuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Création'), 
        ('UPDATE', 'Modification'), 
        ('DELETE', 'Suppression'), 
        ('LOGIN', 'Connexion'),
        ('EXPORT', 'Export'),
        ('BACKUP', 'Sauvegarde'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='accueil_audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Log d'audit"
        verbose_name_plural = "Logs d'audit"

    def __str__(self):
        return f"{self.action} - {self.model_name} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"

# === SYMPTOMS & DIAGNOSIS ===
class Symptom(models.Model):
    name = models.CharField(max_length=100)
    name_ful = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, choices=[
        ('FEVER', 'Fièvre'),
        ('PAIN', 'Douleur'),
        ('RESPIRATORY', 'Respiratoire'),
        ('DIGESTIVE', 'Digestif'),
        ('SKIN', 'Peau'),
        ('OTHER', 'Autre'),
    ])
    severity_level = models.CharField(max_length=10, choices=[
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyen'),
        ('HIGH', 'Élevé'),
    ], default='MEDIUM')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Symptôme"
        verbose_name_plural = "Symptômes"

    def __str__(self):
        return f"{self.name}"

class DiagnosisRecommendation(models.Model):
    symptoms = models.ManyToManyField(Symptom, related_name='diagnoses')
    condition_fr = models.CharField(max_length=200)
    condition_ful = models.CharField(max_length=200)
    recommendation_fr = models.TextField()
    recommendation_ful = models.TextField()
    urgency_level = models.CharField(max_length=10, choices=[
        ('LOW', 'Peu urgent'),
        ('MEDIUM', 'Urgent'),
        ('HIGH', 'Très urgent'),
    ], default='MEDIUM')
    related_medications = models.ManyToManyField(Medication, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['condition_fr']
        verbose_name = "Recommandation de diagnostic"
        verbose_name_plural = "Recommandations de diagnostic"

    def __str__(self):
        return f"{self.condition_fr}"