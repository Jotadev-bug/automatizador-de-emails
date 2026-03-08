import os
import pandas as pd
from faker import Faker
import random

# Inicializar Faker
fake = Faker()

# Definir ruta de salida
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'synthetic_emails.csv')

def generate_invoice_email():
    """Genera Clase 0: Facturas"""
    company = fake.company()
    amount = round(random.uniform(50.0, 5000.0), 2)
    iban = fake.iban()
    subject = f"Factura #{fake.random_int(min=1000, max=9999)} de {company}"
    body = f"Estimado Cliente,\n\nAdjunto encontrará la factura de su compra reciente.\nMonto a pagar: ${amount}\nPor favor transfiera al IBAN: {iban}\n\nGracias,\nEquipo de Finanzas de {company}\n(Adjunto: factura_{fake.random_int(min=1000, max=9999)}.pdf)"
    return subject, body, 0

def generate_urgent_email():
    """Genera Clase 1: Urgente/Soporte"""
    issues = ["Caída del Sistema", "No puedo iniciar sesión", "Sitio web caído", "¡Pago fallido! ¡Urgente!"]
    subject = random.choice(issues)
    body = f"Hola soporte,\n\n{fake.paragraph(nb_sentences=3)}\n¡Esto es críticamente urgente! Estamos perdiendo dinero porque el sistema está desconectado.\nPor favor arréglenlo de inmediato.\n\nSaludos,\n{fake.name()}."
    return subject, body, 1

def generate_noise_email():
    """Genera Clase 2: Ruido/Boletines (Newsletters)"""
    subject = fake.catch_phrase()
    body = f"¡Hola!\n\n{fake.paragraph(nb_sentences=4)}\n\nNo te pierdas nuestra última promo. Haz clic aquí para suscribirte y ahorrar 20% en nuevos productos.\n\nPara cancelar la suscripción, haz clic en el enlace de abajo.\nSaludos,\nEl Equipo de Marketing"
    return subject, body, 2

def build_dataset(num_records=1000):
    os.makedirs(DATA_DIR, exist_ok=True)
    records = []
    
    # Generar conjunto de datos equilibrado
    generators = [generate_invoice_email, generate_urgent_email, generate_noise_email]
    
    for _ in range(num_records):
        generator = random.choice(generators)
        subject, body, label = generator()
        records.append({
            'sender': fake.email(),
            'subject': subject,
            'body': body,
            'label': label
        })
        
    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Generados {num_records} correos sintéticos y guardados en {OUTPUT_FILE}")

if __name__ == "__main__":
    build_dataset(1500)
