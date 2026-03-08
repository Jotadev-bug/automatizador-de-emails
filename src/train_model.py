import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Importaciones relativas desde la carpeta local src
from preprocessing import TextPreprocessor

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'synthetic_emails.csv')

# Rutas de artefactos para serialización
MODEL_PATH = os.path.join(DATA_DIR, 'svm_model.pkl')
VECTORIZER_PATH = os.path.join(DATA_DIR, 'tfidf_vectorizer.pkl')

def train_and_serialize():
    if not os.path.exists(DATA_FILE):
        print(f"Error: No se encontró {DATA_FILE}. Ejecuta data_generation.py primero.")
        return

    print("Cargando conjunto de datos sintético...")
    df = pd.read_csv(DATA_FILE)

    print("Preprocesando datos de texto...")
    preprocessor = TextPreprocessor()
    
    # Enriquecer la representación textual uniendo el asunto y el cuerpo
    df['content'] = df['subject'] + " " + df['body']
    df['cleaned_content'] = df['content'].apply(preprocessor.process)

    X = df['cleaned_content']
    y = df['label']

    print("Vectorizando Texto vía TF-IDF...")
    # Limita el tamaño del espacio de características para rendimiento
    vectorizer = TfidfVectorizer(max_features=5000)
    X_vec = vectorizer.fit_transform(X)

    # División 80/20 entrenamiento/prueba (train/test split)
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

    print("Entrenando modelo LinearSVC...")
    model = LinearSVC(random_state=42)
    model.fit(X_train, y_train)

    print("\n--- Métricas de Evaluación ---")
    predictions = model.predict(X_test)
    target_names = ['Clase 0 (Facturas)', 'Clase 1 (Urgente)', 'Clase 2 (Ruido)']
    
    try:
        print(classification_report(y_test, predictions, target_names=target_names))
        print("Matriz de Confusión:")
        print(confusion_matrix(y_test, predictions))
    except Exception as e:
        # Respaldo si el mapeo del objetivo no coincide perfectamente durante la generación sintética parcial
        print(f"Problema generando métricas: {e}")

    # Guardar (persistir) el modelo y el vectorizador para el bucle de ejecución de la Fase 4
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"\nModelo y vectorizador guardados en {DATA_DIR}/")

if __name__ == "__main__":
    train_and_serialize()
