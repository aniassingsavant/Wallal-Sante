import os
import uuid
import requests # Pour faire des requêtes HTTP à l'Overpass API
import logging
from .serializers import ProfileSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from geopy.distance import geodesic # Pour calculer les distances si nécessaire
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import google.generativeai as genai
from gtts import gTTS

# configure gemini via .env
GEN_API_KEY = os.getenv("GEMINI_API_KEY")
# ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

if not GEN_API_KEY:
    raise RuntimeError("GEMINI_API_KEY manquante dans .env")
genai.configure(api_key=GEN_API_KEY)

# Nouveau prompt détaillé
PROMPT_TEMPLATE = """
Tu es 'Wallal Santé', un assistant de santé virtuel pour la population
de Maroua et de la région de l'Extrême-Nord du Cameroun.

Tes règles SONT ABSOLUES et tu ne dois JAMAIS y déroger :

1. Tu n'es PAS un médecin. NE JAMAIS DIAGNOSTIQUER une maladie. NE
JAMAIS PRESCRIRE de médicament.

2. Tu dois TOUJOURS recommander de consulter un professionnel de santé
(médecin, infirmier, centre de santé) pour tout problème médical.

3. Tes réponses doivent être SIMPLES, COURTES et FACILES à comprendre.

4. Réponds TOUJOURS dans la même langue que la question de
l'utilisateur (Français ou Fulfulde). Si c'est en Fulfulde, utilise le
dialecte de l'Adamawa (Maroua).

5. Tes connaissances doivent se concentrer sur les problèmes de santé
locaux : paludisme, choléra, malnutrition, hygiène de base, santé
maternelle et infantile.

6. Si un utilisateur demande de traduire ses symptômes pour un médecin,
reformule-les de manière claire en français. Exemple : Si l'utilisateur
dit "Reedu am na wela" (J'ai mal au ventre en Fulfulde), tu peux
proposer la traduction "Symptôme à décrire au médecin : Douleur
abdominale".

---

Voici des exemples de la manière dont tu DOIS répondre :

---

Exemple 1:

Question: J'ai une très forte fièvre et mal à la tête, qu'est-ce que j'ai ?

Ta réponse: Avoir une forte fièvre peut être le signe de quelque chose
de sérieux, comme le paludisme. Je ne peux pas vous dire ce que vous
avez, seul un médecin le peut. Allez vite au centre de santé le plus
proche.

Exemple 2:

Question: Mi dilli reedu. Mi yara lekki ki? (J'ai la diarrhée. Je prends quel médicament ?)

Ta réponse: Dilli reedu na waawi wonde aybe. Mi waawataa hokkude ma
lekki. Ko ɓuri jam, yah haa lopital. Yaran ndiyam laaɓɗam sanne ngam taa
cellal ma ɓilla. (La diarrhée peut être dangereuse. Je ne peux pas te
donner de médicament. Le mieux est d'aller à l'hôpital. Bois beaucoup
d'eau propre pour ne pas te déshydrater.)

Exemple 3:

Question: Quels sont les symptômes du choléra ?

Ta réponse: Les signes principaux du choléra sont une diarrhée très
forte (comme de l'eau de riz) et des vomissements. C'est une urgence.
Il faut aller au centre de santé le plus proche immédiatement et boire
beaucoup d'eau propre.

Exemple 4:

Question: Noa welti? (Comment ça va ?)

Ta réponse: Jam tan. Holno mballitumi ma hande dow cellal ma? (Je vais
bien. Comment puis-je t'aider aujourd'hui concernant ta santé ?)

---

Maintenant, réponds à la nouvelle question de l'utilisateur en respectant
TOUTES ces règles et en t'inspirant de ces exemples.

---

Question de l'utilisateur: {question_utilisateur}
"""

def generate_ai(text_prompt):
    model = genai.GenerativeModel("gemini-2.5-pro")
    response = model.generate_content(text_prompt)
    return response.text

def save_tts_to_file(text, lang='fr'):
    # media dir
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)
    filename = f"response_{uuid.uuid4().hex[:10]}.mp3"
    path = os.path.join(settings.MEDIA_ROOT, filename)
    # gTTS does not support "ff" (fulfulde) language codes; we use fr fallback
    tts_lang = 'fr' if lang == 'fr' or lang == 'ff' else lang
    tts = gTTS(text, lang=tts_lang)
    tts.save(path)
    return filename  # retourne le nom du fichier (serveur servira /media/filename)

@api_view(['GET'])
@permission_classes([AllowAny])
def status(request):
    return Response({"status": "ok"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyse(request):

    text = request.data.get("message")  
    lang = request.data.get("language", "fr")  

    if not text:  
        return Response({"error": "Message manquant"}, status=400)  

    # Utilisation du nouveau prompt détaillé
    prompt = PROMPT_TEMPLATE.format(question_utilisateur=text)

    try:  
        ai_text = generate_ai(prompt)

        # si langue demandée est fulfulde ('ff'), demander la traduction à Gemini
        #translated_text = ai_text
        #if lang == 'ff':
            #translate_prompt = f"Traduis en Fulfulde (dialecte Adamawa, Cameroun) : {ai_text}"
            #translated_text = generate_ai(translate_prompt)

        # générer audio et retourner URL
        filename = save_tts_to_file(ai_text, lang=lang)
        audio_url = request.build_absolute_uri(f"/media/{filename}")

        return Response({  
            "original_text": ai_text,  
            #"translated_text": translated_text,  
            "audio_url": audio_url  
        }) 
        response = requests.post("http://api.externe.com/analyse", ...)
    except Exception as e:  
       
    # AFFICHEZ L'ERREUR RÉELLE DANS LE TERMINAL
        # print(f"ERREUR LORS DE L'APPEL EXTERNE : {e}") 
    #logging.error(f"Erreur de connexion externe: {e}") # Encore mieux si vous utilisez logging

    # Renvoyez une erreur plus spécifique si possible
    #return JsonResponse({"error": f"Échec de la connexion au service externe: {str(e)}"}, status=500)
        #return Response({"error": str(e)}, status=500)
        # Affiche l'erreur complète dans votre terminal (powershell)
        logging.error(f"ERREUR DÉTAILLÉE DANS LA VUE 'analyse': {e}")
        
        # Renvoie l'erreur au client (Thunder Client)
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def translate(request):
   # if not check_token(request):
    #    return Response({"error": "Accès non autorisé"}, status=401)

    text = request.data.get("text")  
    target = request.data.get("target_lang", "ff")  
    if not text:  
        return Response({"error": "Texte manquant"}, status=400)  

    try:  
        prompt = f"Traduis ce texte en {target} : {text}"
        translated = generate_ai(prompt)
        return Response({"translated": translated})
    except Exception as e:  
        return Response({"error": str(e)}, status=500)

# Configuration Overpass
OVERPASS_URL = "http://overpass-api.de/api/interpreter"
RADIUS_KM = 5  # Rayon de recherche de 5 km autour de l'utilisateur

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def find_hospitals_osm(request):
    """
    Trouve les hôpitaux les plus proches en utilisant OpenStreetMap (OSM) via Overpass API.
    """
    
    #if not check_token(request):
     #   return Response({"error": "Accès non autorisé"}, status=401)

    lat_str = request.data.get('latitude')
    lng_str = request.data.get('longitude')

    if not lat_str or not lng_str:
        return Response({"error": "Latitude ou longitude manquante"}, status=400)
    
    try:
        lat = float(lat_str)
        lng = float(lng_str)
        user_coords = (lat, lng)
    except ValueError:
        return Response({"error": "Coordonnées invalides"}, status=400)

    try:
        # 1. Requête Overpass
        # Cette requête (QL) cherche tous les Points d'Intérêt (POI) tagués comme hôpitaux (amenity=hospital)
        # ou cliniques (amenity=clinic) dans un rayon de 5000 mètres (5 km) autour des coordonnées de l'utilisateur.
        overpass_query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:{RADIUS_KM * 1000},{lat},{lng});
          node["amenity"="clinic"](around:{RADIUS_KM * 1000},{lat},{lng});
        );
        out center;
        """

        response = requests.post(OVERPASS_URL, data={'data': overpass_query})
        response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP
        data = response.json()

        # 2. Traitement et formatage des résultats
        hospitals = []
        for element in data.get('elements', []):
            if element['type'] == 'node':
                place_lat = element.get('lat')
                place_lon = element.get('lon')
                
                # Calcul de la distance entre l'utilisateur et l'hôpital
                hospital_coords = (place_lat, place_lon)
                distance = geodesic(user_coords, hospital_coords).km
                
                # Ajout à la liste
                hospitals.append({
                    'name': element.get('tags', {}).get('name', 'Centre de Santé Inconnu'),
                    'address': element.get('tags', {}).get('addr:full', 'Non spécifiée'),
                    'distance_km': round(distance, 1), # Arrondi à 1 décimale
                    'location': {'lat': place_lat, 'lng': place_lon}
                })

        # Trier les résultats par distance (les plus proches en premier)
        hospitals.sort(key=lambda x: x['distance_km'])

        # 3. Réponse finale au Frontend (limité à 5 résultats)
        return Response({"hospitals": hospitals[:5]}) 

    except requests.exceptions.RequestException as e:
        return Response({"error": f"Erreur de connexion à l'API OpenStreetMap: {e}"}, status=503)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Vue pour récupérer ou mettre à jour le profil de l'utilisateur connecté.
    GET: Retourne les données de profil.
    POST: Met à jour les données de profil.
    """
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Cas de sécurité si le signal a échoué (rare), on crée le profil
        profile = Profile.objects.create(user=request.user)

    if request.method == 'GET':
        # Lire le profil
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Mettre à jour le profil avec les données envoyées par Flutter
        # Le deuxième argument 'profile' est l'instance à modifier
        serializer = ProfileSerializer(profile, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            # Retourne les données mises à jour
            return Response(serializer.data, status=200)
        
        # Erreur de validation (ex: l'âge n'est pas un nombre)
        return Response(serializer.errors, status=400)