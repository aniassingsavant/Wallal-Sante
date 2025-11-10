
import os
import uuid
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import google.generativeai as genai
from gtts import gTTS

# configure gemini via .env
GEN_API_KEY = os.getenv("GEMINI_API_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

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

# simple decorator pour vérifier le token Authorization
def check_token(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth.split(" ", 1)[1]
    return token == ACCESS_TOKEN

def generate_ai(text_prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
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
@permission_classes([AllowAny])
def analyse(request):
    # sécuriser par token
    if not check_token(request):
        return Response({"error": "Accès non autorisé"}, status=401)

    text = request.data.get("message")  
    lang = request.data.get("language", "fr")  # 'fr' ou 'ff'  

    if not text:  
        return Response({"error": "Message manquant"}, status=400)  

    # Utilisation du nouveau prompt détaillé
    prompt = PROMPT_TEMPLATE.format(question_utilisateur=text)

    try:  
        ai_text = generate_ai(prompt)

        # si langue demandée est fulfulde ('ff'), demander la traduction à Gemini
        translated_text = ai_text
        if lang == 'ff':
            translate_prompt = f"Traduis en Fulfulde (dialecte Adamawa, Cameroun) : {ai_text}"
            translated_text = generate_ai(translate_prompt)

        # générer audio et retourner URL
        filename = save_tts_to_file(translated_text, lang=lang)
        audio_url = request.build_absolute_uri(f"/media/{filename}")

        return Response({  
            "original_text": ai_text,  
            "translated_text": translated_text,  
            "audio_url": audio_url  
        })  
    except Exception as e:  
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def translate(request):
    if not check_token(request):
        return Response({"error": "Accès non autorisé"}, status=401)

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
