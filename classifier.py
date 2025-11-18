# classifier.py

import os
from dotenv import load_dotenv
from openai import OpenAI

# 1) Charger les variables d'environnement depuis .env
load_dotenv()

# 2) Récupérer la clé Groq
api_key = os.getenv("GROQ_API_KEY")

# 3) Vérifier que la clé existe bien
if not api_key:
    raise ValueError(" La variable GROQ_API_KEY n'est pas définie dans le fichier .env")

# 4) Créer un client cinfigurer par Groq*
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",  # endpoint Groq compatible OpenAI :contentReference[oaicite:0]{index=0}
)

CATEGORIES = [
    "probleme_technique_informatique",
    "demande_administrative",
    "probleme_acces_authentification",
    "demande_support_utilisateur",
    "bug_ou_dysfonctionnement_service"
]

URGENCES = [
    "anodine",
    "faible",
    "moderee",
    "elevee",
    "critique"
]


def classify_ticket(subject: str, body: str) -> str:
    """
    Prend le sujet et le corps d'un mail,
    renvoie un JSON (texte) avec categorie, urgence, synthese.
    """

    system_prompt = f"""
Tu es un agent de tri de tickets par e-mail.

Ton travail :
1. Lire le sujet et le contenu du mail.
2. Choisir UNE seule catégorie dans cette liste exacte :
   {CATEGORIES}
3. Choisir UN seul niveau d'urgence dans cette liste exacte :
   {URGENCES}
4. Produire une synthèse courte (1 à 3 phrases) en français,
   compréhensible par un humain.

Réponds STRICTEMENT au format JSON, sans texte autour, par exemple :
{{
  "categorie": "demande_administrative",
  "urgence": "moderee",
  "synthese": "..."
}}
"""

    user_prompt = f"""
Voici un ticket reçu par e-mail.

Sujet :
\"\"\"{subject}\"\"\"

Contenu :
\"\"\"{body}\"\"\"

Analyse ce ticket et renvoie le JSON demandé.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # modèle valide Groq
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content
        return content

    except Exception as e:
        print(" Erreur lors de l'appel à Groq :")
        print(type(e))
        print(e)
        # si la réponse HTTP est dispo, on l'affiche
        if hasattr(e, "response") and hasattr(e.response, "text"):
            print("\n--- Contenu brut de la réponse HTTP ---")
            print(e.response.text)
        # On renvoie un message pour que le programme ne plante pas complètement
        return '{"erreur": "appel_groq_impossible"}'

