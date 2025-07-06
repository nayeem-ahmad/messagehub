import smtplib
from email.mime.text import MIMEText
import requests
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import time
import random
import socket
from requests.exceptions import RequestException, ConnectionError, Timeout

def retry_with_backoff(func, max_retries=3, base_delay=1, max_delay=60):
    """
    Retry a function with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                raise e
            
            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            print(f"Retrying in {delay:.1f} seconds...")
            time.sleep(delay)

def send_email_smtp(smtp_settings, sender, password, recipient, subject, body, sender_name=None):
    def _send():
        server = None
        try:
            server = smtplib.SMTP(smtp_settings["server"], smtp_settings["port"])
            server.settimeout(30)  # 30 second timeout
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
            return True
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass  # Ignore errors when closing connection
    
    return retry_with_backoff(_send, max_retries=3)


def send_email_sendgrid(api_key, sender, recipient, subject, body, sender_name=None):
    def _send():
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
        
        # Use timeout and retry-friendly session
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code >= 400:
            raise Exception(f"SendGrid error: {response.status_code} {response.text}")
        return response
    
    return retry_with_backoff(_send, max_retries=3)


def send_email_ses(access_key, secret_key, region, sender, recipient, subject, body, sender_name=None):
    def _send():
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
            return response
        except (BotoCoreError, ClientError) as e:
            raise Exception(f"SES error: {e}")
    
    return retry_with_backoff(_send, max_retries=3)


def send_email(method, settings, sender, password, recipient, subject, body, sender_name=None):
    """
    method: 'smtp', 'sendgrid', or 'ses'
    settings: dict with relevant keys for the method
    sender_name: optional display name for the sender
    """
    try:
        if method == 'smtp':
            return send_email_smtp(settings, sender, password, recipient, subject, body, sender_name)
        elif method == 'sendgrid':
            return send_email_sendgrid(settings['sendgrid_api_key'], sender, recipient, subject, body, sender_name)
        elif method == 'ses':
            return send_email_ses(settings['ses_access_key'], settings['ses_secret_key'], settings['ses_region'], sender, recipient, subject, body, sender_name)
        else:
            raise ValueError(f"Unknown email method: {method}")
    except Exception as e:
        # Log the final failure
        print(f"Failed to send email to {recipient} after all retries: {str(e)}")
        raise e

def check_internet_connection():
    """
    Check if internet connection is available
    """
    try:
        # Try to connect to Google's DNS
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def send_email_with_connection_check(method, settings, sender, password, recipient, subject, body, sender_name=None):
    """
    Send email with internet connection check
    """
    # First check if internet is available
    if not check_internet_connection():
        print("No internet connection detected. Waiting for connection...")
        
        # Wait for internet connection (up to 5 minutes)
        for i in range(30):  # 30 attempts, 10 seconds each = 5 minutes
            time.sleep(10)
            if check_internet_connection():
                print("Internet connection restored!")
                break
            print(f"Still waiting for internet connection... ({i+1}/30)")
        else:
            raise Exception("No internet connection available after 5 minutes of waiting")
    
    # Proceed with sending email
    return send_email(method, settings, sender, password, recipient, subject, body, sender_name)