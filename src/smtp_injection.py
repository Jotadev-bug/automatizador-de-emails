import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'synthetic_emails.csv')

def inject_emails(num_emails=50):
    """Dispatches a random subset of synthetic emails to the test inbox."""
    if not all([SMTP_HOST, SMTP_PORT, EMAIL_USER, EMAIL_PASS]):
        print("Error: SMTP credentials not properly configured in .env")
        return

    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found. Run data_generation.py first.")
        return

    df = pd.read_csv(DATA_FILE)
    # Take a random sample without replacement
    sample_df = df.sample(n=min(num_emails, len(df)))

    # Connect to SMTP server
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        
        count = 0
        for _, row in sample_df.iterrows():
            msg = MIMEMultipart()
            msg['From'] = row['sender']
            msg['To'] = EMAIL_USER
            msg['Subject'] = row['subject']
            
            # Attach the body using text/plain
            msg.attach(MIMEText(row['body'], 'plain'))
            
            server.send_message(msg)
            count += 1
            print(f"Sent email {count}/{num_emails}: {row['subject']}")
            
        server.quit()
        print(f"Successfully injected {count} emails.")
    except Exception as e:
        print(f"SMTP Error: {str(e)}")

if __name__ == "__main__":
    inject_emails(20) # Inject 20 emails by default for testing
