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

# Configuración de Registros (Logging)
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
        
        # Comprobar si se debe utilizar OAuth2
        creds = get_oauth2_credentials()
        if creds and creds.valid:
            logging.info("Usando autenticación OAuth2")
            self.access_token = get_oauth2_string(self.user, creds.token)
        
        if not self.host or not self.user:
            logging.error("Falta servidor o usuario IMAP en .env")
            exit(1)
        if not self.password and not self.access_token:
            logging.error("Falta método de autenticación (No hay contraseña ni token OAuth2 válido)")
            exit(1)
            
        logging.info("Cargando Artefactos de ML...")
        try:
            self.model = joblib.load(MODEL_PATH)
            self.vectorizer = joblib.load(VECTORIZER_PATH)
        except Exception as e:
            logging.error(f"Fallo al cargar modelos: {e}. ¿Ejecutaste train_model.py?")
            exit(1)
            
        self.client = EmailClient(self.host, self.user, password=self.password, access_token=self.access_token)
        self.preprocessor = TextPreprocessor()
        self.db_session = init_db()

    def process_inbox(self):
        logging.info("Comprobando nuevos correos...")
        emails = self.client.fetch_unseen_emails()
        
        if not emails:
            logging.info("No se hallaron correos nuevos.")
            return

        for email in emails:
            uid = email['uid']
            content = email['subject'] + " " + email['body']
            
            # Preprocesamiento
            cleaned = self.preprocessor.process(content)
            
            # Vectorización
            vec = self.vectorizer.transform([cleaned])
            
            # Predicción
            pred = self.model.predict(vec)[0]
            
            class_map = {0: "INVOICE", 1: "URGENT", 2: "NOISE"}
            logging.info(f"Correo UID {uid} -> Predicción: {class_map.get(pred, 'DESCONOCIDO')}")
            
            # Enrutamiento
            self.client.route_email(uid, pred)
            
            action = class_map.get(pred, 'UNKNOWN')
            logging.info(f"Correo UID {uid} -> Acción completada. Guardado en BDD.")
            
            # Persistir a BD
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
                logging.error(f"Error guardando en la BDD: {e}")
                self.db_session.rollback()

def execute_job():
    daemon = EmailDaemon()
    daemon.process_inbox()

if __name__ == "__main__":
    logging.info("Iniciando Demonio Automatizado IA")
    # Ejecutar una vez al inicio
    execute_job()
    
    # Programar cada 5 minutos
    schedule.every(5).minutes.do(execute_job)
    
    logging.info("Programador corriendo. Presiona Ctrl+C para salir.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Demonio detenido por usuario.")
