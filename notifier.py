import smtplib
from email.mime.text import MIMEText

def notify_contact(email, message):
    msg = MIMEText(message)
    msg["Subject"] = "Safety Alert"
    msg["From"] = "no-reply@evaluator"
    msg["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login("your_email", "your_password")
        smtp.send_message(msg)

    return True

# Can also be AWS SNS or Twilio