import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Relative imports from the local src folder
from preprocessing import TextPreprocessor

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'synthetic_emails.csv')

# Artifact paths for serialization
MODEL_PATH = os.path.join(DATA_DIR, 'svm_model.pkl')
VECTORIZER_PATH = os.path.join(DATA_DIR, 'tfidf_vectorizer.pkl')

def train_and_serialize():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found. Run data_generation.py first.")
        return

    print("Loading synthetic dataset...")
    df = pd.read_csv(DATA_FILE)

    print("Preprocessing text data...")
    preprocessor = TextPreprocessor()
    
    # Enrich the textual representation by joining subject and body
    df['content'] = df['subject'] + " " + df['body']
    df['cleaned_content'] = df['content'].apply(preprocessor.process)

    X = df['cleaned_content']
    y = df['label']

    print("Vectorizing Text via TF-IDF...")
    # Limits feature space size for performance
    vectorizer = TfidfVectorizer(max_features=5000)
    X_vec = vectorizer.fit_transform(X)

    # 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

    print("Training LinearSVC model...")
    model = LinearSVC(random_state=42)
    model.fit(X_train, y_train)

    print("\n--- Evaluation Metrics ---")
    predictions = model.predict(X_test)
    target_names = ['Class 0 (Invoices)', 'Class 1 (Urgent)', 'Class 2 (Noise)']
    
    try:
        print(classification_report(y_test, predictions, target_names=target_names))
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, predictions))
    except Exception as e:
        # Fallback if target mapping doesn't match perfectly during partial synthetic generation
        print(f"Metrics generation issue: {e}")

    # Persist the model and vectorizer for Phase 4 execution loop
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"\nSaved model and vectorizer to {DATA_DIR}/")

if __name__ == "__main__":
    train_and_serialize()
