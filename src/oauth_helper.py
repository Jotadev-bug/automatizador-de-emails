import os
import json
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']
TOKEN_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'token.json')
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')

def get_oauth2_credentials():
    """Gets valid user credentials from storage, or triggers the OAuth2 flow to get new ones."""
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            logging.error(f"Error reading token: {e}")

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                logging.error(f"Missing {CREDENTIALS_PATH}. Please download it from Google Cloud Console.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            # This triggers a local web server to handle redirect from Google
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return creds

def get_oauth2_string(user_email, access_token):
    """
    Generates the IMAP XOAUTH2 format string required for authentication.
    Format: user={email}^Aauth=Bearer {token}^A^A
    """
    auth_string = f"user={user_email}\1auth=Bearer {access_token}\1\1"
    return auth_string

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    creds = get_oauth2_credentials()
    if creds:
        print("OAuth2 Flow Completed Successfully. Token generated and saved.")
    else:
        print("OAuth2 Flow Failed. Ensure you have credentials.json in the project root.")
