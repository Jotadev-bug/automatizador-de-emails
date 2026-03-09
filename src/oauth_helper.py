import os
import json
import logging
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

# Si modificas estos alcances (scopes), elimina el archivo token.json.
SCOPES = ['https://mail.google.com/']
TOKEN_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'token.json')
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')

def get_oauth2_credentials():
    """Obtiene credenciales válidas del almacenamiento, o inicia el flujo OAuth2 para obtener unas nuevas."""
    if not GOOGLE_AUTH_AVAILABLE:
        logging.warning("Dependencias de Google OAuth2 no instaladas. Recurriendo a contraseña en .env.")
        return None
        
    creds = None
    # El archivo token.json guarda los tokens de acceso y refresco del usuario
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            logging.error(f"Error leyendo token: {e}")

    # Si no hay credenciales (válidas) disponibles, permitir que el usuario inicie sesión.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                logging.error(f"Falta {CREDENTIALS_PATH}. Por favor, descárgalo desde la Google Cloud Console.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            # Esto inicia un servidor web local para manejar la redirección de Google
            creds = flow.run_local_server(port=0)
            
        # Guardar las credenciales para la próxima ejecución
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return creds

def get_oauth2_string(user_email, access_token):
    """
    Genera la cadena de formato IMAP XOAUTH2 requerida para la autenticación.
    Formato: user={email}^Aauth=Bearer {token}^A^A
    """
    auth_string = f"user={user_email}\1auth=Bearer {access_token}\1\1"
    return auth_string

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    creds = get_oauth2_credentials()
    if creds:
        print("Flujo OAuth2 Completado Exitosamente. Token generado y guardado.")
    else:
        print("Fallo en Flujo OAuth2. Asegúrate de tener credentials.json en la raíz del proyecto.")
