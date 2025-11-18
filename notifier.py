import os
import boto3
from botocore.exceptions import ClientError

ses_client = boto3.client(
    "ses",
    region_name="eu-west-1"
    # aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    # aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

FROM_EMAIL = os.getenv("SES_FROM_EMAIL")
SUBJECT = "Safety Alert"

def notify_contact(to_email, message):
    if not FROM_EMAIL:
        raise ValueError("FROM_EMAIL is not set or is None")
    try:
        response = ses_client.send_email(
            Source=FROM_EMAIL, # has to be confirmed - aws ses verify-email-identity --email-address no-reply@myapp.com --region eu-west-1
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": SUBJECT}, # 'Safety Alert'
                "Body": {"Text": {"Data": message}}
            }
        )
        print("Email sent! Message ID:", response['MessageId'])
        return True
    except ClientError as e:
        print("Error sending email:", e.response['Error']['Message'])
        return False

# recipient = "friend@example.com"
# msg = "Alert: individual showing high risk behavior."
# notify_contact(recipient, msg)

# import smtplib
# from email.mime.text import MIMEText
#
# def notify_contact(email, message):
#     msg = MIMEText(message)
#     msg["Subject"] = "Safety Alert"
#     msg["From"] = "no-reply@evaluator"
#     msg["To"] = email
#
#     with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
#         smtp.starttls()
#         smtp.login("your_email", "your_password")
#         smtp.send_message(msg)
#
#     return True
#
# # Can also be AWS SNS or Twilio