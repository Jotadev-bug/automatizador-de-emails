import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'synthetic_emails.csv')

def inject_emails(num_emails=50):
    """Envía un subconjunto aleatorio de correos sintéticos a la bandeja de prueba."""
    if not all([SMTP_HOST, SMTP_PORT, EMAIL_USER, EMAIL_PASS]):
        print("Error: Las credenciales SMTP no están bien configuradas en .env")
        return

    if not os.path.exists(DATA_FILE):
        print(f"Error: No se encontró {DATA_FILE}. Ejecuta data_generation.py primero.")
        return

    df = pd.read_csv(DATA_FILE)
    # Tomar una muestra aleatoria sin reemplazo
    sample_df = df.sample(n=min(num_emails, len(df)))

    # Conectar al servidor SMTP
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
            
            # Adjuntar el cuerpo usando text/plain
            msg.attach(MIMEText(row['body'], 'plain'))
            
            server.send_message(msg)
            count += 1
            print(f"Correo enviado {count}/{num_emails}: {row['subject']}")
            
        server.quit()
        print(f"Se inyectaron con éxito {count} correos.")
    except Exception as e:
        print(f"Error SMTP: {str(e)}")

if __name__ == "__main__":
    inject_emails(20) # Inyectar 20 correos por defecto para pruebas
