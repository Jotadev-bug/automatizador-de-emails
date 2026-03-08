from imap_tools import MailBox, A
from bs4 import BeautifulSoup

def get_email_payload(msg):
    """Lógica de respaldo para extraer el texto plano del cuerpo."""
    if msg.text:
        return msg.text
    elif msg.html:
        soup = BeautifulSoup(msg.html, "html.parser")
        return soup.get_text()
    return ""

class EmailClient:
    def __init__(self, host, user, password=None, access_token=None):
        self.host = host
        self.user = user
        self.password = password
        self.access_token = access_token
        
    def _login(self):
        """Función auxiliar para establecer la conexión al buzón usando Contraseña u OAuth2."""
        mailbox = MailBox(self.host)
        if self.access_token:
            return mailbox.xoauth2(self.user, self.access_token)
        elif self.password:
            return mailbox.login(self.user, self.password)
        else:
            raise ValueError("Se debe proporcionar una contraseña o un access_token para la autenticación.")

    def fetch_unseen_emails(self):
        """Obtiene correos que no han sido leídos aún."""
        emails = []
        try:
            with self._login() as mailbox:
                # Apuntar a la carpeta INBOX y filtrar por no leídos (UNSEEN)
                for msg in mailbox.fetch(A(seen=False)):
                    emails.append({
                        'uid': msg.uid,
                        'message_id': msg.headers.get('message-id', [''])[0],
                        'sender': msg.from_,
                        'date': msg.date,
                        'subject': msg.subject,
                        'body': get_email_payload(msg)
                    })
        except Exception as e:
            print(f"Error en Obtención IMAP: {e}")
        return emails

    def route_email(self, uid, predicted_class):
        """Mueve o marca un correo con bandera basado en la clase predicha del modelo."""
        try:
            with self._login() as mailbox:
                if predicted_class == 0:
                    # Mover a 1_INVOICES (Nota: Debes crear esta carpeta en tu proveedor de correo)
                    mailbox.move(uid, '1_INVOICES')
                elif predicted_class == 1:
                    # Aplicar bandera \Flagged (Destacado) y mover a '2_URGENT'
                    mailbox.flag(uid, '\\Flagged', True)
                    mailbox.move(uid, '2_URGENT')
                elif predicted_class == 2:
                    # Aplicar bandera \Seen (Leído) y mover a Papelera (o eliminar)
                    mailbox.flag(uid, '\\Seen', True)
                    mailbox.delete(uid)
        except Exception as e:
            print(f"Error de Enrutamiento IMAP (UID {uid}): {e}")
