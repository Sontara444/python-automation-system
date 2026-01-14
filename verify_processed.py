
from src.gmail_service import get_gmail_service
from datetime import datetime

msg_id = '19515063c2d361bd'
service = get_gmail_service()
msg = service.users().messages().get(userId='me', id=msg_id).execute()
headers = msg.get('payload', {}).get('headers', [])
date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
internal_date = int(msg.get('internalDate', 0)) / 1000
readable_internal = datetime.fromtimestamp(internal_date).strftime('%Y-%m-%d %H:%M:%S')
print(f"ID: {msg_id} | Date: {date} | Internal: {readable_internal}")
