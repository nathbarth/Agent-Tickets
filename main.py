# main.py

from gmail_reader import get_last_emails
from classifier import classify_ticket

# Quelques e-mails de test pour travailler même si Gmail bloque
SAMPLE_EMAILS = [
    {
        "subject": "Incident de sécurité : fuite de données sensibles détectée",
        "body": """
Bonjour,

Une anomalie a été détectée dans le système d’authentification interne.
Un accès non autorisé a été enregistré vers la base de données des clients
(table « clients_confidentiels ») à 02h12. Les données sensibles
(numéros de sécurité sociale, coordonnées bancaires) ont pu être extraites.

Nous avons immédiatement bloqué l’accès et lancé une enquête.
Je sollicite votre intervention urgente pour analyser les logs,
appliquer un patch de sécurité et informer les parties concernées.
Merci de traiter cette demande en priorité absolue.

Cordialement,
Élodie Rousseau.
""",
    },
    {
        "subject": "Demande d'attestation de scolarité",
        "body": """
Bonjour,

Je voudrais obtenir une attestation de scolarité pour l'année 2024-2025
afin de la transmettre à mon employeur.
Pouvez-vous me l'envoyer par e-mail dès que possible ?

Merci beaucoup,
Nathalie
""",
    },
]


def main():
    # 1) Essayer de récupérer les e-mails réels via Gmail
    emails = get_last_emails(max_results=3)

    # 2) Si Gmail renvoie rien (quota dépassé, boîte vide...), on bascule sur les e-mails de test
    if not emails:
        print(" Aucun e-mail récupéré depuis Gmail.")
        print(" Utilisation des e-mails de test à la place.\n")
        emails = SAMPLE_EMAILS

    # 3) Pour chaque e-mail, on appelle ton agent IA Groq
    for mail in emails:
        print("\n" + "=" * 60)
        print(" Sujet du mail :", mail["subject"])
        print(" Corps du mail :")
        print(mail["body"])

        print("\n Analyse de l'agent :")
        result_json = classify_ticket(mail["subject"], mail["body"])
        print(result_json)


if __name__ == "__main__":
    main()
