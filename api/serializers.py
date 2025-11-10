from rest_framework import serializers
# Importez votre modèle Profile que vous venez de créer dans models.py
from .models import Profile 

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer pour la lecture et la mise à jour des données de profil.
    """
    
    # NOTE: L'utilisateur (user) lui-même n'est pas inclus ici car 
    # nous le gérons via request.user dans la vue.
    class Meta:
        model = Profile
        # Liste de tous les champs que Flutter peut lire et écrire
        fields = [
            'age', 
            'sex', 
            'is_pregnant', 
            'chronic_illness', 
            'medical_history'
        ]
        # Assurez-vous que les noms des champs correspondent exactement à models.py