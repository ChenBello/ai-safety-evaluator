import os
import smtplib
from email.message import EmailMessage
import json

# load contacts list (optional) - you can also keep this JSON inline
CONTACTS = {
    "support": {
        "name": "ער\"ן",
        "phone": "1201",
        "description": "קווי סיוע נפשיים"
    },
    "nettl": {
        "name": "נט\"ל",
        "phone": "1200",
        "description": "קו סיוע לנפגעי תקיפה מינית"
    },
    "local_contact": {
        "name": "Contact Person",
        "email": os.environ.get("ESCALATION_EMAIL")  # set in .env
    }
}

def build_intervention_payload(category, explanation, text, presigned_url=None):
    """
    Return dict with recommended actions and contacts based on category / severity.
    """
    payload = {
        "category": category,
        "explanation": explanation,
        "recommended_actions": [],
        "contacts": []
    }

    # simple rules — expand as needed
    if category and ("self-harm" in category.lower() or "suicid" in category.lower()):
        payload["recommended_actions"].append("Contact emergency mental health support immediately")
        payload["contacts"].append(CONTACTS["support"])
    elif category and ("violence" in category.lower() or "abuse" in category.lower()):
        payload["recommended_actions"].append("Consider reporting to local authorities / victims support")
        payload["contacts"].append(CONTACTS["nettl"])
    else:
        payload["recommended_actions"].append("Offer resources and option to contact a support person")
        payload["contacts"].append(CONTACTS["local_contact"])

    # include a link to the item (if available)
    if presigned_url:
        payload["item_url"] = presigned_url

    return payload

def send_escalation_email(subject, body, to_email=None):
    """
    Simple SMTP sender. By default reads SMTP_* vars from env.
    Alternatively you can implement SendGrid and swap here.
    """
    SMTP_HOST = os.environ.get("SMTP_HOST")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER")
    SMTP_PASS = os.environ.get("SMTP_PASS")
    FROM_EMAIL = os.environ.get("FROM_EMAIL", SMTP_USER)

    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and to_email):
        # not configured - return False but do not raise
        return False, "SMTP not configured or recipient missing"

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        return True, "Email sent"
    except Exception as e:
        return False, str(e)
