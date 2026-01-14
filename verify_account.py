
from src.gmail_service import get_gmail_service

def verify_account():
    service = get_gmail_service()
    profile = service.users().getProfile(userId='me').execute()
    print(f"Authenticated Email: {profile.get('emailAddress')}")
    print(f"Total Messages: {profile.get('messagesTotal')}")
    print(f"Threads Total: {profile.get('threadsTotal')}")

if __name__ == '__main__':
    verify_account()
