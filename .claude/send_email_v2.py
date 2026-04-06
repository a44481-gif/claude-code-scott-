"""
Send email via 163.com SMTP with explicit SSL
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Configuration
SMTP_SERVER = 'smtp.163.com'
SMTP_PORT = 465
SENDER = 'h13751019800@163.com'
AUTH_CODE = 'FZQAXDZUHDWQHUIO'
RECIPIENT = 'h13751019800@163.com'

def send_email():
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Daily PSU Sales Report - 2026-04-02'
    msg['From'] = SENDER
    msg['To'] = RECIPIENT
    
    # Read HTML report
    with open(r'd:\claude mini max 2.7\.claude\psu_daily_report_20260402.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Attach HTML
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    # Create SSL context
    context = ssl.create_default_context()
    
    print('Connecting to SMTP server...')
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            print('Logging in...')
            server.login(SENDER, AUTH_CODE)
            print('Sending email...')
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            print('SUCCESS: Email sent to ' + RECIPIENT)
            return True
    except Exception as e:
        print('ERROR: ' + str(e))
        return False

if __name__ == '__main__':
    send_email()