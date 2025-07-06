#!/usr/bin/env python3
"""
Background Campaign Processor for MessageHub
Processes email and SMS campaigns independently of the main application
"""

import sys
import os
import sqlite3
import json
import time
import threading
import logging
from datetime import datetime
import argparse
import signal

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from services import email_utils
from features.common import get_settings, DB_FILE

class CampaignProcessor:
    def __init__(self, campaign_id, campaign_type='email'):
        self.campaign_id = campaign_id
        self.campaign_type = campaign_type
        self.running = True
        self.db_path = DB_FILE
        self.logger = self._setup_logging()
        
        # Handle shutdown signals
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _setup_logging(self):
        """Setup logging for the background process"""
        log_filename = f"campaign_processor_{self.campaign_type}_{self.campaign_id}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    def update_campaign_status(self, status, details=None):
        """Update campaign status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            if self.campaign_type == 'email':
                cursor.execute("""
                    UPDATE email_campaigns 
                    SET status = ?, last_updated = ?, processing_details = ?
                    WHERE id = ?
                """, (status, timestamp, details, self.campaign_id))
            else:
                cursor.execute("""
                    UPDATE sms_campaigns 
                    SET status = ?, last_updated = ?, processing_details = ?
                    WHERE id = ?
                """, (status, timestamp, details, self.campaign_id))
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update campaign status: {e}")
    
    def log_progress(self, message, level="info"):
        """Log progress with both file and database logging"""
        if level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
        else:
            self.logger.info(message)
            
        # Update status in database
        self.update_campaign_status("running", message)
    
    def process_email_campaign(self):
        """Process email campaign in background"""
        try:
            self.log_progress("🚀 Starting email campaign processor")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get campaign details
            cursor.execute("SELECT name, subject, body FROM email_campaigns WHERE id = ?", (self.campaign_id,))
            campaign = cursor.fetchone()
            
            if not campaign:
                self.log_progress("❌ Campaign not found", "error")
                self.update_campaign_status("failed", "Campaign not found")
                return False
                
            campaign_name, subject, body = campaign
            self.log_progress(f"📧 Processing campaign: {campaign_name}")
            
            # Get campaign contacts
            cursor.execute("""
                SELECT c.id, c.name, c.email, c.mobile 
                FROM contacts c
                JOIN email_campaign_contacts ecc ON c.id = ecc.contact_id
                WHERE ecc.campaign_id = ? AND c.email IS NOT NULL AND c.email != ''
                ORDER BY c.name
            """, (self.campaign_id,))
            
            contacts = cursor.fetchall()
            total_contacts = len(contacts)
            
            if total_contacts == 0:
                self.log_progress("⚠️ No valid contacts found", "warning")
                self.update_campaign_status("completed", "No valid contacts")
                return True
                
            self.log_progress(f"📊 Processing {total_contacts} contacts")
            
            # Load settings
            settings = get_settings()
            email_method = settings.get('email_method', 'SMTP')
            
            # Validate email settings
            if not self._validate_email_settings(settings, email_method):
                self.log_progress("❌ Invalid email settings", "error")
                self.update_campaign_status("failed", "Invalid email settings")
                return False
            
            sent_count = 0
            failed_count = 0
            
            # Process each contact
            for i, (contact_id, name, email, mobile) in enumerate(contacts):
                if not self.running:
                    self.log_progress("⏹️ Campaign stopped by user")
                    self.update_campaign_status("stopped", f"Processed {sent_count}/{total_contacts}")
                    break
                    
                try:
                    # Personalize content
                    personalized_subject = self._personalize_content(subject, name, email, mobile)
                    personalized_body = self._personalize_content(body, name, email, mobile)
                    
                    # Send email
                    success = self._send_email(settings, email_method, email, personalized_subject, personalized_body)
                    
                    if success:
                        # Record success
                        cursor.execute("""
                            INSERT INTO email_campaign_history 
                            (campaign_id, contact_id, timestamp, status, personalized_subject, personalized_body)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (self.campaign_id, contact_id, datetime.now(), "sent", personalized_subject, personalized_body))
                        
                        sent_count += 1
                        progress = int((i + 1) / total_contacts * 100)
                        self.log_progress(f"✅ {progress}% - Sent to {name or 'Unknown'} ({email}) - {sent_count}/{total_contacts}")
                    else:
                        failed_count += 1
                        
                    # Commit after each email
                    conn.commit()
                    
                    # Delay to avoid spam detection and rate limiting
                    if self.running:
                        time.sleep(2)
                        
                except Exception as e:
                    # Record failure
                    cursor.execute("""
                        INSERT INTO email_campaign_history 
                        (campaign_id, contact_id, timestamp, status, error)
                        VALUES (?, ?, ?, ?, ?)
                    """, (self.campaign_id, contact_id, datetime.now(), "failed", str(e)))
                    
                    failed_count += 1
                    self.log_progress(f"❌ Failed to send to {name or 'Unknown'} ({email}): {str(e)}", "error")
                    conn.commit()
            
            # Final status
            if self.running:
                final_message = f"🎉 Campaign completed! Sent: {sent_count}, Failed: {failed_count}"
                self.log_progress(final_message)
                self.update_campaign_status("completed", final_message)
            
            conn.close()
            return True
            
        except Exception as e:
            error_msg = f"💥 Campaign processing error: {str(e)}"
            self.log_progress(error_msg, "error")
            self.update_campaign_status("failed", error_msg)
            return False
    
    def _validate_email_settings(self, settings, method):
        """Validate email configuration"""
        if method == "SMTP":
            required = ['sender_email', 'sender_pwd', 'smtp_server', 'smtp_port']
            return all(settings.get(key) for key in required)
        elif method == "SendGrid":
            return bool(settings.get('sendgrid_api_key'))
        elif method == "Amazon SES":
            required = ['ses_access_key', 'ses_secret_key', 'ses_region']
            return all(settings.get(key) for key in required)
        return False
    
    def _personalize_content(self, content, name, email, mobile):
        """Personalize content with contact details"""
        if not content:
            return content
            
        personalized = content
        personalized = personalized.replace("{{name}}", name or "")
        personalized = personalized.replace("{{email}}", email or "")
        personalized = personalized.replace("{{mobile}}", mobile or "")
        return personalized
    
    def _send_email(self, settings, method, recipient, subject, body):
        """Send individual email with error handling"""
        try:
            if method == "SMTP":
                email_utils.send_smtp_email(
                    settings.get('smtp_server'),
                    int(settings.get('smtp_port', 587)),
                    settings.get('sender_email'),
                    settings.get('sender_pwd'),
                    recipient,
                    subject,
                    body,
                    settings.get('sender_name', '')
                )
            elif method == "SendGrid":
                email_utils.send_sendgrid_email(
                    settings.get('sendgrid_api_key'),
                    settings.get('sender_email'),
                    recipient,
                    subject,
                    body
                )
            elif method == "Amazon SES":
                email_utils.send_ses_email(
                    settings.get('ses_access_key'),
                    settings.get('ses_secret_key'),
                    settings.get('ses_region'),
                    settings.get('sender_email'),
                    recipient,
                    subject,
                    body
                )
            return True
            
        except Exception as e:
            self.logger.error(f"Email sending failed: {e}")
            return False
    
    def process_sms_campaign(self):
        """Process SMS campaign in background"""
        try:
            self.log_progress("📱 Starting SMS campaign processor")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get campaign details
            cursor.execute("SELECT name, message FROM sms_campaigns WHERE id = ?", (self.campaign_id,))
            campaign = cursor.fetchone()
            
            if not campaign:
                self.log_progress("❌ SMS Campaign not found", "error")
                self.update_campaign_status("failed", "Campaign not found")
                return False
                
            campaign_name, message = campaign
            self.log_progress(f"📱 Processing SMS campaign: {campaign_name}")
            
            # Get campaign contacts
            cursor.execute("""
                SELECT c.id, c.name, c.email, c.mobile 
                FROM contacts c
                JOIN sms_campaign_contacts scc ON c.id = scc.contact_id
                WHERE scc.campaign_id = ? AND c.mobile IS NOT NULL AND c.mobile != ''
                ORDER BY c.name
            """, (self.campaign_id,))
            
            contacts = cursor.fetchall()
            total_contacts = len(contacts)
            
            if total_contacts == 0:
                self.log_progress("⚠️ No valid contacts with mobile numbers found", "warning")
                self.update_campaign_status("completed", "No valid contacts")
                return True
                
            self.log_progress(f"📊 Processing {total_contacts} contacts")
            
            # Load settings
            settings = get_settings()
            sms_method = settings.get('sms_method', 'Twilio')
            
            # Validate SMS settings
            if not self._validate_sms_settings(settings, sms_method):
                self.log_progress("❌ Invalid SMS settings", "error")
                self.update_campaign_status("failed", "Invalid SMS settings")
                return False
            
            sent_count = 0
            failed_count = 0
            
            # Process each contact
            for i, (contact_id, name, email, mobile) in enumerate(contacts):
                if not self.running:
                    self.log_progress("⏹️ SMS Campaign stopped by user")
                    self.update_campaign_status("stopped", f"Processed {sent_count}/{total_contacts}")
                    break
                    
                try:
                    # Personalize content
                    personalized_message = self._personalize_content(message, name, email, mobile)
                    
                    # Send SMS
                    success = self._send_sms(settings, sms_method, mobile, personalized_message)
                    
                    if success:
                        # Record success
                        cursor.execute("""
                            INSERT INTO sms_campaign_history 
                            (campaign_id, contact_id, timestamp, status, personalized_message)
                            VALUES (?, ?, ?, ?, ?)
                        """, (self.campaign_id, contact_id, datetime.now(), "sent", personalized_message))
                        
                        sent_count += 1
                        progress = int((i + 1) / total_contacts * 100)
                        self.log_progress(f"✅ {progress}% - Sent to {name or 'Unknown'} ({mobile}) - {sent_count}/{total_contacts}")
                    else:
                        failed_count += 1
                        
                    # Commit after each SMS
                    conn.commit()
                    
                    # Delay to avoid rate limiting
                    if self.running:
                        time.sleep(3)  # Longer delay for SMS to avoid rate limits
                        
                except Exception as e:
                    # Record failure
                    cursor.execute("""
                        INSERT INTO sms_campaign_history 
                        (campaign_id, contact_id, timestamp, status, error)
                        VALUES (?, ?, ?, ?, ?)
                    """, (self.campaign_id, contact_id, datetime.now(), "failed", str(e)))
                    
                    failed_count += 1
                    self.log_progress(f"❌ Failed to send to {name or 'Unknown'} ({mobile}): {str(e)}", "error")
                    conn.commit()
            
            # Final status
            if self.running:
                final_message = f"🎉 SMS Campaign completed! Sent: {sent_count}, Failed: {failed_count}"
                self.log_progress(final_message)
                self.update_campaign_status("completed", final_message)
            
            conn.close()
            return True
            
        except Exception as e:
            error_msg = f"💥 SMS Campaign processing error: {str(e)}"
            self.log_progress(error_msg, "error")
            self.update_campaign_status("failed", error_msg)
            return False
    
    def _validate_sms_settings(self, settings, method):
        """Validate SMS configuration"""
        if method == "Twilio":
            required = ['twilio_account_sid', 'twilio_auth_token', 'twilio_phone_number']
            return all(settings.get(key) for key in required)
        elif method == "AWS SNS":
            required = ['aws_access_key', 'aws_secret_key', 'aws_region']
            return all(settings.get(key) for key in required)
        return False
    
    def _send_sms(self, settings, method, recipient, message):
        """Send individual SMS with error handling"""
        try:
            if method == "Twilio":
                # Import Twilio here to avoid dependency issues
                from twilio.rest import Client
                
                account_sid = settings.get('twilio_account_sid')
                auth_token = settings.get('twilio_auth_token')
                from_number = settings.get('twilio_phone_number')
                
                client = Client(account_sid, auth_token)
                message_obj = client.messages.create(
                    body=message,
                    from_=from_number,
                    to=recipient
                )
                
                self.logger.info(f"SMS sent successfully. SID: {message_obj.sid}")
                
            elif method == "AWS SNS":
                import boto3
                
                sns = boto3.client(
                    'sns',
                    aws_access_key_id=settings.get('aws_access_key'),
                    aws_secret_access_key=settings.get('aws_secret_key'),
                    region_name=settings.get('aws_region')
                )
                
                response = sns.publish(
                    PhoneNumber=recipient,
                    Message=message
                )
                
                self.logger.info(f"SMS sent successfully. MessageId: {response['MessageId']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"SMS sending failed: {e}")
            return False
def main():
    """Main entry point for background processor"""
    parser = argparse.ArgumentParser(description='MessageHub Background Campaign Processor')
    parser.add_argument('campaign_id', type=int, help='Campaign ID to process')
    parser.add_argument('--type', choices=['email', 'sms'], default='email', help='Campaign type')
    parser.add_argument('--pid-file', help='Write process ID to file')
    
    args = parser.parse_args()
    
    # Write PID file if requested
    if args.pid_file:
        with open(args.pid_file, 'w') as f:
            f.write(str(os.getpid()))
    
    # Create and run processor
    processor = CampaignProcessor(args.campaign_id, args.type)
    
    try:
        if args.type == 'email':
            success = processor.process_email_campaign()
        else:
            success = processor.process_sms_campaign()
            
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        processor.log_progress("🛑 Campaign interrupted by user")
        processor.update_campaign_status("stopped", "Interrupted by user")
        sys.exit(130)
    except Exception as e:
        processor.log_progress(f"💥 Unexpected error: {e}", "error")
        processor.update_campaign_status("failed", f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Clean up PID file
        if args.pid_file and os.path.exists(args.pid_file):
            try:
                os.remove(args.pid_file)
            except:
                pass

if __name__ == "__main__":
    main()
