import os
import time
import schedule
import logging
from dotenv import load_dotenv
import joblib

from email_client import EmailClient
from preprocessing import TextPreprocessor
from database import init_db, EmailLog
from oauth_helper import get_oauth2_credentials, get_oauth2_string

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'execution.log'))
    ]
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
MODEL_PATH = os.path.join(DATA_DIR, 'svm_model.pkl')
VECTORIZER_PATH = os.path.join(DATA_DIR, 'tfidf_vectorizer.pkl')

class EmailDaemon:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv('EMAIL_HOST')
        self.user = os.getenv('EMAIL_USER')
        self.password = os.getenv('EMAIL_PASS')
        self.access_token = None
        
        # Check if OAuth2 should be used
        creds = get_oauth2_credentials()
        if creds and creds.valid:
            logging.info("Using OAuth2 for Authentication")
            self.access_token = get_oauth2_string(self.user, creds.token)
        
        if not self.host or not self.user:
            logging.error("IMAP host or user missing in .env")
            exit(1)
        if not self.password and not self.access_token:
            logging.error("Authentication method missing (No password and no valid OAuth2 token)")
            exit(1)
            
        logging.info("Loading ML Artifacts...")
        try:
            self.model = joblib.load(MODEL_PATH)
            self.vectorizer = joblib.load(VECTORIZER_PATH)
        except Exception as e:
            logging.error(f"Failed to load models: {e}. Did you run train_model.py?")
            exit(1)
            
        self.client = EmailClient(self.host, self.user, password=self.password, access_token=self.access_token)
        self.preprocessor = TextPreprocessor()
        self.db_session = init_db()

    def process_inbox(self):
        logging.info("Checking for new emails...")
        emails = self.client.fetch_unseen_emails()
        
        if not emails:
            logging.info("No new emails found.")
            return

        for email in emails:
            uid = email['uid']
            content = email['subject'] + " " + email['body']
            
            # Preprocess
            cleaned = self.preprocessor.process(content)
            
            # Vectorize
            vec = self.vectorizer.transform([cleaned])
            
            # Predict
            pred = self.model.predict(vec)[0]
            
            class_map = {0: "INVOICE", 1: "URGENT", 2: "NOISE"}
            logging.info(f"Email UID {uid} -> Predicted: {class_map.get(pred, 'UNKNOWN')}")
            
            # Route
            self.client.route_email(uid, pred)
            
            action = class_map.get(pred, 'UNKNOWN')
            logging.info(f"Email UID {uid} -> Routing action completed. Logged to DB.")
            
            # Persist to database
            try:
                log_entry = EmailLog(
                    message_id=str(uid),
                    sender=email['sender'],
                    predicted_class=int(pred),
                    action_taken=action
                )
                self.db_session.add(log_entry)
                self.db_session.commit()
            except Exception as e:
                logging.error(f"Failed to save to database: {e}")
                self.db_session.rollback()

def execute_job():
    daemon = EmailDaemon()
    daemon.process_inbox()

if __name__ == "__main__":
    logging.info("Starting AI Email Automation Daemon")
    # Run once immediately
    execute_job()
    
    # Schedule every 5 minutes
    schedule.every(5).minutes.do(execute_job)
    
    logging.info("Scheduler running. Press Ctrl+C to exit.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Daemon stopped by user.")
