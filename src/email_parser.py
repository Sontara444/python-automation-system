
import base64
import re
from datetime import datetime
from bs4 import BeautifulSoup

def parse_email(message):
    """Parses a Gmail API message object into a flattened dictionary."""
    payload = message.get('payload', {})
    headers = payload.get('headers', [])
    
    data = {
        'From': '',
        'Subject': '',
        'Date': '',
        'Content': ''
    }
    
    for header in headers:
        name = header.get('name')
        if name == 'From':
            data['From'] = header.get('value')
        elif name == 'Subject':
            data['Subject'] = header.get('value')
        elif name == 'Date':
            data['Date'] = header.get('value')
            
    data['Content'] = get_email_body(payload)
    return data

def get_email_body(payload):
    """Recursively extracts body, prioritizing plain text but falling back to HTML stripping."""
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                return decode_base64(part['body'].get('data', ''))
        
        for part in payload['parts']:
            if part.get('mimeType') == 'text/html':
                html_content = decode_base64(part['body'].get('data', ''))
                return strip_html(html_content)
                
            if 'parts' in part:
                 res = get_email_body(part)
                 if res: return res

    elif payload.get('mimeType') == 'text/plain':
        return decode_base64(payload['body'].get('data', ''))

    elif payload.get('mimeType') == 'text/html':
        html_content = decode_base64(payload['body'].get('data', ''))
        return strip_html(html_content)
        
    return ""

def strip_html(html_content):
    """Strips HTML tags to return clean text."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def decode_base64(data):
    """Decodes base64url encoded string."""
    if not data:
        return ""
    count = len(data) % 4
    if count:
        data += '=' * (4 - count)
    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
