import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings
import pickle


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class GmailService:
    """
    Service class to handle Gmail API operations for sending OTP emails.
    """
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth2.
        Token will be saved and reused for subsequent requests.
        """
        creds = None
        credentials_dir = os.path.join(settings.BASE_DIR, '.credentials')
        
        # Ensure credentials directory exists
        os.makedirs(credentials_dir, exist_ok=True)
        
        token_path = os.path.join(credentials_dir, 'gmail_token.pickle')
        credentials_path = os.path.join(credentials_dir, 'gmail_credentials.json')
        
        # Load saved credentials if they exist
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials are invalid or don't exist, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"Gmail credentials file not found at {credentials_path}. "
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.credentials = creds
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service
    
    def create_message(self, to, subject, body):
        """
        Create an email message.
        
        Args:
            to: Email recipient
            subject: Email subject
            body: Email body (HTML or plain text)
        
        Returns:
            Dictionary containing the message
        """
        message = MIMEText(body, 'html')
        message['to'] = to
        message['subject'] = subject
        
        # Get sender email from settings or use 'me' (authenticated user)
        sender = getattr(settings, 'GMAIL_SENDER_EMAIL', 'me')
        message['from'] = sender
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
    def send_email(self, to, subject, body):
        """
        Send an email using Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (HTML)
        
        Returns:
            Sent message object
        """
        try:
            if not self.service:
                self.authenticate()
            
            message = self.create_message(to, subject, body)
            sent_message = self.service.users().messages().send(
                userId='me', body=message
            ).execute()
            
            return sent_message
        
        except HttpError as error:
            raise Exception(f"An error occurred while sending email: {error}")
    
    def send_otp_email(self, user_email, username, otp_code):
        """
        Send OTP verification email to user.
        
        Args:
            user_email: User's email address
            username: User's username
            otp_code: 6-digit OTP code
        
        Returns:
            Sent message object
        """
        subject = "Your Login Verification Code"
        
        # HTML email template
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Poppins', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #ffffff;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .otp-box {{
                    background-color: #f8f9fa;
                    border: 2px dashed #667eea;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .otp-code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 8px;
                    margin: 10px 0;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 14px;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Login Verification</h1>
                </div>
                <div class="content">
                    <p>Hello <strong>{username}</strong>,</p>
                    <p>You requested to log in to your Inventory Management System account. Please use the verification code below to complete your login:</p>
                    
                    <div class="otp-box">
                        <div style="font-size: 14px; color: #6c757d; margin-bottom: 10px;">Your Verification Code</div>
                        <div class="otp-code">{otp_code}</div>
                        <div style="font-size: 14px; color: #6c757d; margin-top: 10px;">Valid for 10 minutes</div>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong> If you did not request this code, please ignore this email and ensure your account is secure.
                    </div>
                    
                    <p>This code will expire in <strong>10 minutes</strong>.</p>
                </div>
                <div class="footer">
                    <p>Inventory Management System<br>
                    This is an automated message, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body)


# Global instance
gmail_service = GmailService()
