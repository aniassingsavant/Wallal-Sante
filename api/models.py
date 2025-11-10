from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError("L'utilisateur doit avoir une adresse email.")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

class Profile(models.Model):
    # Liaison vers votre modèle User personnalisé ci-dessus
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    
    # --- Champs Personnels ---
    age = models.IntegerField(null=True, blank=True)
    
    SEX_CHOICES = [
        ('MALE', 'Homme'),
        ('FEMALE', 'Femme'),
        ('OTHER', 'Autre'),
    ]
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, null=True, blank=True)
    
    PREGNANCY_CHOICES = [
        ('YES', 'Oui'),
        ('NO', 'Non'),
        ('UNKNOWN', 'Ne se prononce pas'),
    ]
    is_pregnant = models.CharField(
        max_length=10, 
        choices=PREGNANCY_CHOICES, 
        default='UNKNOWN', 
        null=True, blank=True
    )
    
    # --- Historique Médical ---
    chronic_illness = models.TextField(
        blank=True, null=True, 
        help_text="Maladies chroniques connues, ex: Diabète, Hypertension, Asthme"
    )
    medical_history = models.TextField(
        blank=True, null=True, 
        help_text="Antécédents médicaux pertinents, ex: Allergie pénicilline, opération du cœur"
    )

    def __str__(self):
        return f'{self.user.email} Profile'

# --- SIGNALS pour la Création Automatique ---

# Crée automatiquement un profil lorsque l'utilisateur est enregistré
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# S'assure que le profil est sauvegardé quand l'utilisateur est mis à jour
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Vérifie si le profil existe avant d'essayer de le sauvegarder
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Si le signal est déclenché par une mise à jour d'un utilisateur sans profil, on le crée
        Profile.objects.create(user=instance)