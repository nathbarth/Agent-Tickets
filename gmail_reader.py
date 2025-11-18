# gmail_reader.py
"""
Ce module s'occupe de :
1. Se connecter à l'API Gmail avec OAuth (credentials.json)
2. Récupérer les derniers e-mails (sujet + corps)
"""

import os
import base64

from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Scopes : les permissions que l'on demande à Gmail
# Ici : lire les mails (readonly suffit pour commencer)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    """
    Crée et renvoie un objet 'service' Gmail authentifié.
    - Si un token existe (token.json), on le réutilise.
    - Sinon, on lance le flux OAuth (fenêtre navigateur) pour se connecter.
    """

    creds = None

    # 1) Si on a déjà un token (première connexion déjà faite), on le charge
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # 2) Si pas de credentials OU invalides, on relance le flux OAuth
    if not creds or not creds.valid:
        # Si le token a expiré mais possède un "refresh token", on le rafraîchit
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Sinon, on lance le flux de connexion basé sur le fichier credentials.json
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            # Cela ouvre une fenêtre de navigateur pour te faire connecter à ton compte Gmail
            creds = flow.run_local_server(port=0)

        # 3) On sauvegarde les credentials dans token.json pour les prochaines fois
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # 4) On construit le service Gmail avec les credentials
    service = build("gmail", "v1", credentials=creds)
    return service


def get_last_emails(max_results=5):
    """
    Récupère les 'max_results' derniers e-mails de la boîte de réception.
    Retourne une liste de dictionnaires :
      [{ "id": ..., "subject": ..., "body": ... }, ...]
    """

    service = get_gmail_service()

    try:
        # 1) On récupère la liste des derniers messages de la boîte de réception
        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], maxResults=max_results)
            .execute()
        )
    except HttpError as e:
        # Si c'est une erreur de quota (429), on affiche un message clair
        if e.resp.status == 429:
            print(" Gmail - quota dépassé (erreur 429).")
            print("Détail :", e)
            # On retourne une liste vide pour que le programme ne plante pas
            return []
        # Sinon, on relance l'erreur normale
        raise

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        m = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="full")
            .execute()
        )

        headers = m["payload"].get("headers", [])
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"),
            "(Sans sujet)",
        )

        body = ""
        payload = m["payload"]

        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    data = part["body"].get("data")
                    if data:
                        body = base64.urlsafe_b64decode(data).decode("utf-8")
                        break
        else:
            data = payload["body"].get("data")
            if data:
                body = base64.urlsafe_b64decode(data).decode("utf-8")

        emails.append(
            {
                "id": msg["id"],
                "subject": subject,
                "body": body,
            }
        )

    return emails



# Petit test si on lance directement ce fichier :
if __name__ == "__main__":
    mails = get_last_emails(3)
    for mail in mails:
        print("=" * 60)
        print("Sujet :", mail["subject"])
        print("Corps :")
        print(mail["body"])
