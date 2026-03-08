from imap_tools import MailBox, A
from bs4 import BeautifulSoup

def get_email_payload(msg):
    """Fallback logic to extract plain text body."""
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
        """Helper to establish the mailbox connection using either Password or OAuth2."""
        mailbox = MailBox(self.host)
        if self.access_token:
            return mailbox.xoauth2(self.user, self.access_token)
        elif self.password:
            return mailbox.login(self.user, self.password)
        else:
            raise ValueError("Either password or access_token must be provided for authentication.")

    def fetch_unseen_emails(self):
        """Fetch emails that haven't been read yet."""
        emails = []
        try:
            with self._login() as mailbox:
                # Target the INBOX folder and filter for UNSEEN
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
            print(f"IMAP Fetch Error: {e}")
        return emails

    def route_email(self, uid, predicted_class):
        """Moves or flags an email based on the model's predicted class."""
        try:
            with self._login() as mailbox:
                if predicted_class == 0:
                    # Move to 1_INVOICES (Note: You must create this folder in your email provider)
                    mailbox.move(uid, '1_INVOICES')
                elif predicted_class == 1:
                    # Apply \Flagged (Starred) flag and move to '2_URGENT'
                    mailbox.flag(uid, '\\Flagged', True)
                    mailbox.move(uid, '2_URGENT')
                elif predicted_class == 2:
                    # Apply \Seen flag and move to Trash (or delete)
                    mailbox.flag(uid, '\\Seen', True)
                    mailbox.delete(uid)
        except Exception as e:
            print(f"IMAP Routing Error (UID {uid}): {e}")
