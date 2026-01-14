
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from tenacity import retry, stop_after_attempt, wait_exponential
import config

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_credentials():
    """Gets valid user credentials from storage or runs OAuth flow."""
    creds = None
    token_path = os.path.join('credentials', 'token.json')
    credentials_path = os.path.join('credentials', 'credentials.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, config.SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Credentials not found at {credentials_path}.")
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, config.SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    return creds

def get_gmail_service():
    """Builds and returns the Gmail service."""
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_unread_emails(service, max_results=None):
    """Fetches list of unread emails from Inbox."""
    try:
        results = service.users().messages().list(
            userId='me', 
            q='is:unread label:INBOX',
            maxResults=max_results
        ).execute()
        return results.get('messages', [])
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_email_details(service, msg_id):
    """Gets full details of a specific email."""
    try:
        return service.users().messages().get(
            userId='me', 
            id=msg_id,
            format='full'
        ).execute()
    except Exception as e:
        print(f"An error occurred fetching message {msg_id}: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def mark_email_as_read(service, msg_id):
    """Removes the UNREAD label from an email."""
    try:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
    except Exception as e:
        print(f"Failed to mark email {msg_id} as read: {e}")
        raise
