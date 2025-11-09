# conseils/models.py (ajouter ces modèles)
from django.db import models
from django.contrib.auth.models import User

class HealthEstablishment(models.Model):
    name = models.CharField(max_length=200)
    TYPE_CHOICES = [
        ('HOSPITAL', 'Hôpital'),
        ('CLINIC', 'Clinique'),
        ('DISPENSARY', 'Dispensaire'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    region = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AdminAuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='conseils_audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)