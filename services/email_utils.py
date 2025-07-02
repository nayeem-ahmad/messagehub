import smtplib
from email.mime.text import MIMEText
import requests
import boto3
from botocore.exceptions import BotoCoreError, ClientError

def send_email_smtp(smtp_settings, sender, password, recipient, subject, body, sender_name=None):
    server = smtplib.SMTP(smtp_settings["server"], smtp_settings["port"])
    server.starttls()
    server.login(sender, password)
    msg = MIMEText(body)
    msg['Subject'] = subject
    # Format the From field with display name if provided
    if sender_name:
        msg['From'] = f'"{sender_name}" <{sender}>'
    else:
        msg['From'] = sender
    msg['To'] = recipient
    server.sendmail(sender, recipient, msg.as_string())
    server.quit()


def send_email_sendgrid(api_key, sender, recipient, subject, body, sender_name=None):
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    from_field = {"email": sender}
    if sender_name:
        from_field["name"] = sender_name
    
    data = {
        "personalizations": [
            {"to": [{"email": recipient}]}
        ],
        "from": from_field,
        "subject": subject,
        "content": [
            {"type": "text/plain", "value": body}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code >= 400:
        raise Exception(f"SendGrid error: {response.status_code} {response.text}")


def send_email_ses(access_key, secret_key, region, sender, recipient, subject, body, sender_name=None):
    try:
        client = boto3.client(
            'ses',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        # Format the Source field with display name if provided
        source = f'"{sender_name}" <{sender}>' if sender_name else sender
        
        response = client.send_email(
            Source=source,
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
    except (BotoCoreError, ClientError) as e:
        raise Exception(f"SES error: {e}")


def send_email(method, settings, sender, password, recipient, subject, body, sender_name=None):
    """
    method: 'smtp', 'sendgrid', or 'ses'
    settings: dict with relevant keys for the method
    sender_name: optional display name for the sender
    """
    if method == 'smtp':
        send_email_smtp(settings, sender, password, recipient, subject, body, sender_name)
    elif method == 'sendgrid':
        send_email_sendgrid(settings['sendgrid_api_key'], sender, recipient, subject, body, sender_name)
    elif method == 'ses':
        send_email_ses(settings['ses_access_key'], settings['ses_secret_key'], settings['ses_region'], sender, recipient, subject, body, sender_name)
    else:
        raise ValueError(f"Unknown email method: {method}")