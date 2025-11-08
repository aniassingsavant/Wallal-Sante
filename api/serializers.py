from django.contrib.auth.models import User
from rest_framework import serializers

# Serializer pour l'inscription des utilisateurs
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}} # Le mdp n'est pas renvoyé

    def create(self, validated_data):
        # Utilise create_user pour que le mot de passe soit "hashé" (sécurisé)
        user = User.objects.create_user(
            validated_data['username'], 
            validated_data['email'], 
            validated_data['password']
        )
        return user