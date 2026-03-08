# MVP de Automatización de Correos Electrónicos con IA

Este proyecto contiene el MVP completo para el sistema de enrutamiento inteligente de correos electrónicos delineado en el ROADMAP.
El código ha sido modularizado dentro de la carpeta `src/`.

## Instrucciones de Configuración

Ejecuta estos comandos en tu terminal para inicializar y ejecutar el proyecto:

### 1. Entorno y Dependencias

Primero, crea un entorno virtual e instala las dependencias necesarias:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuración

Renombra el archivo `.env.example` a `.env` y configura tus credenciales de correo para las pruebas.
> **Nota:** Si estás usando Gmail, necesitarás generar una Contraseña de Aplicación (App Password) ya que las contraseñas normales ya no están soportadas para IMAP/SMTP.

```bash
copy .env.example .env
```

Antes de ejecutar el pipeline de Machine Learning, asegúrate de haber creado dos carpetas/etiquetas (labels) en tu bandeja de entrada destino, exactamente con estos nombres:
- `1_INVOICES`
- `2_URGENT`

### 3. Generar Datos Sintéticos

Ejecuta el script generador para crear un conjunto de datos falso de 1,500 correos electrónicos variados. Este conjunto de datos servirá como la "fuente de verdad" (ground-truth) para el modelo de Machine Learning.

```bash
python src/data_generation.py
```

### 4. Entrenar el Modelo NLP

Ejecuta el pipeline de entrenamiento. Este script preprocesará los datos, extraerá las características TF-IDF, entrenará un modelo SVC, lo evaluará y guardará los artefactos binarios dentro de la carpeta `data/`.

```bash
python src/train_model.py
```

### 5. Inyectar Correos de Prueba (Opcional)

Para probar el mecanismo de enrutamiento, usa el script SMTP. Este enviará un subconjunto aleatorio de 20 correos desde el conjunto de datos sintético a tu bandeja de entrada de pruebas.

```bash
python src/smtp_injection.py
```

### 6. Iniciar el Demonio de Ejecución

Inicia el oyente automatizado. Este iniciará sesión en tu servidor IMAP, extraerá los mensajes NO LEÍDOS (UNSEEN), los preprocesará/clasificará, activará las acciones de enrutamiento automatizado (Mover/Marcar/Eliminar) y pausará en un bucle programado (schedule) cada 5 minutos.

```bash
python src/main.py
```
