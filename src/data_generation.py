import os
import pandas as pd
from faker import Faker
import random

# Initialize Faker
fake = Faker()

# Define output path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'synthetic_emails.csv')

def generate_invoice_email():
    """Generates Class 0: Invoices"""
    company = fake.company()
    amount = round(random.uniform(50.0, 5000.0), 2)
    iban = fake.iban()
    subject = f"Invoice #{fake.random_int(min=1000, max=9999)} from {company}"
    body = f"Dear Customer,\n\nPlease find attached the invoice for your recent purchase.\nAmount due: ${amount}\nPlease transfer to IBAN: {iban}\n\nThank you,\n{company} Finance Team\n(Attachment: invoice_{fake.random_int(min=1000, max=9999)}.pdf)"
    return subject, body, 0

def generate_urgent_email():
    """Generates Class 1: Urgent/Support"""
    issues = ["System Outage", "Cannot login", "Website is down", "Payment failed! Urgent!"]
    subject = random.choice(issues)
    body = f"Hello support,\n\n{fake.paragraph(nb_sentences=3)}\nThis is critically urgent! We are losing money because the system is offline.\nPlease fix it immediately.\n\nRegards,\n{fake.name()}."
    return subject, body, 1

def generate_noise_email():
    """Generates Class 2: Noise/Newsletters"""
    subject = fake.catch_phrase()
    body = f"Hi there!\n\n{fake.paragraph(nb_sentences=4)}\n\nDon't miss our latest promo. Click here to subscribe and save 20% on our new products.\n\nTo unsubscribe, click the link below.\nBest,\nThe Marketing Team"
    return subject, body, 2

def build_dataset(num_records=1000):
    os.makedirs(DATA_DIR, exist_ok=True)
    records = []
    
    # Generate balanced dataset
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
    print(f"Generated {num_records} synthetic emails and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    build_dataset(1500)
