# Automatizador Inteligente de Correos | AI Email Automation 🤖📩

> Un pipeline NLP de nivel empresarial que automatiza el enrutamiento de correos electrónicos, reduce el tiempo de procesamiento manual y proporciona observabilidad de datos en tiempo real.

Este proyecto fue desarrollado desde cero para demostrar mi capacidad de llevar un Producto Mínimo Viable (MVP) a un sistema listo para producción, adecuado para un entorno corporativo. Aprovecha el Machine Learning para la clasificación de texto y prácticas modernas de ingeniería de datos para su despliegue y monitorización.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=for-the-badge&logo=Streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)

## ✨ Características Principales y Logros Técnicos

*   **🧠 Pipeline de Machine Learning:** Desarrollé un pipeline NLP personalizado utilizando `scikit-learn` (Vectorización TF-IDF, Eliminación de Stop-words, Lematización) y entrené un Clasificador de Vectores de Soporte (LinearSVC) con más de 1,500 correos sintéticos.
*   **🔌 Integración IMAP Segura:** Implementé un demonio (daemon) automatizado en segundo plano utilizando `imap-tools` que recupera correos no leídos, asegurado por **Google OAuth 2.0 (XOAUTH2)** en lugar de contraseñas de aplicación básicas obsoletas.
*   **📊 Panel de Control Ejecutivo (Observabilidad):** Construí una interfaz web en tiempo real utilizando `Streamlit` y `Plotly` para monitorizar los KPIs del sistema (Correos Procesados, Precisión, Horas Ahorradas) y visualizar las decisiones de enrutamiento.
*   **💾 Gestión de Estado Persistente:** Diseñé un esquema de base de datos relacional usando `SQLAlchemy` y `SQLite` para registrar limpiamente todas las predicciones y acciones, permitiendo políticas de retención de datos.
*   **🐳 Despliegue Contenerizado:** Empaqueté la aplicación de doble servicio (Demonio + Dashboard) en una imagen Docker multi-etapa, orquestada con `Docker Compose` para un despliegue sin problemas en dispositivos como una Raspberry Pi.

## 📁 Arquitectura del Sistema

El código base es modular y está claramente separado en los siguientes componentes:

```bash
📦 automatizador-de-emails
 ┣ 📂 data/                 # Almacena logs SQLite, datos sintéticos y artefactos ML (.pkl)
 ┣ 📂 src/                  # Lógica central de la aplicación
 ┃ ┣ 📜 dashboard.py        # Interfaz Web UI con Streamlit
 ┃ ┣ 📜 data_generation.py  # Generador de dataset sintético basado en Faker
 ┃ ┣ 📜 database.py         # Configuración ORM SQLAlchemy y SQLite
 ┃ ┣ 📜 email_client.py     # Conexión IMAP/SMTP y lógica de enrutamiento
 ┃ ┣ 📜 main.py             # Demonio en segundo plano que orquesta el pipeline ML
 ┃ ┣ 📜 oauth_helper.py     # Lógica de generación de tokens OAuth 2.0 de Google
 ┃ ┣ 📜 preprocessing.py    # Pipeline de limpieza de texto NLP
 ┃ ┣ 📜 smtp_injection.py   # Script de pruebas para despachar correos 
 ┃ ┗ 📜 train_model.py      # Extracción TF-IDF y entrenamiento del modelo LinearSVC
 ┣ 📜 .env.example          # Plantilla de variables de entorno
 ┣ 📜 docker-compose.yml    # Orquestación Docker definiendo ambos servicios
 ┣ 📜 Dockerfile            # Imagen Python ligera multi-etapa
 ┣ 📜 README.md
 ┗ 📜 requirements.txt
```

## 🚀 Guía de Inicio Rápido

Puedes ejecutar este proyecto localmente en tu máquina o desplegarlo a través de Docker.

### Opción A: Entorno de Desarrollo Local

**1. Clonar e Instalar Dependencias**
```bash
git clone https://github.com/Jotadev-bug/automatizador-de-emails.git
cd automatizador-de-emails
python -m venv venv
# En Windows: .\venv\Scripts\activate
# En Unix: source venv/bin/activate
pip install -r requirements.txt
```

**2. Configurar Autenticación**
*   Copia `.env.example` a `.env` y configura tus credenciales.
*   (Opcional pero Recomendado) Descarga `credentials.json` desde la Google Cloud Console y colócalo en la carpeta raíz.
*   Ejecuta el flujo OAuth para generar un token:
    ```bash
    python src/oauth_helper.py
    ```

**3. Preparar los Datos y el Modelo**
Genera los datos de entrenamiento sintéticos y entrena el modelo SVC:
```bash
python src/data_generation.py
python src/train_model.py
```

**4. Ejecutar el Sistema**
Abre dos ventanas de terminal para ejecutar tanto el demonio backend como el panel frontend:
```bash
# Terminal 1: Trabajador en 2do plano procesando correos cada 5 min
python src/main.py

# Terminal 2: Panel de Control Ejecutivo en tiempo real
streamlit run src/dashboard.py
```

### Opción B: Despliegue con Docker (Producción)

Para desplegar todo el sistema (tanto el demonio como el panel web) en contenedores aislados:

```bash
docker-compose up -d --build
```
*El panel estará disponible en `http://localhost:8501`.*

## 📈 Futuros Pasos 
*   **Integración LLM:** Integrar la `API de OpenAI` para extraer automáticamente datos JSON (ej. montos e IBANs) de Facturas y resumir solicitudes urgentes de clientes.
*   **Respuesta Automática:** Conectar con el endpoint `drafts.create` de la API de Gmail para redactar respuestas corteses a consultas de clientes antes de la revisión humana.

---
*Si eres un reclutador revisando este proyecto, no dudes en ponerte en contacto para debatir sobre la arquitectura, los modelos de aprendizaje automático utilizados o las decisiones de diseño del sistema tomadas durante el desarrollo.*
