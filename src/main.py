
import json
import os
import sys
import logging
from datetime import datetime

# Allow running directly as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.gmail_service import get_gmail_service, fetch_unread_emails, get_email_details, mark_email_as_read
from src.sheets_service import get_sheets_service, prepend_to_sheet, trim_sheet
from src.email_parser import parse_email

STATE_FILE = 'state.json'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

def load_processed_ids():
    """Loads processed message IDs from state file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return set(json.load(f))
        except (json.JSONDecodeError, ValueError):
            logging.warning("State file corrupted. Starting fresh.")
    return set()

def save_processed_ids(processed_ids):
    """Saves processed message IDs to state file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(list(processed_ids), f)

def main():
    logging.info("Starting Gmail to Sheets automation...")
    
    try:
        gmail_service = get_gmail_service()
        sheets_service = get_sheets_service()
        logging.info("Successfully authenticated services.")
    except Exception as e:
        logging.error(f"Authentication failed: {e}")
        return

    processed_ids = load_processed_ids()
    messages = fetch_unread_emails(gmail_service, max_results=config.MAX_EMAILS)
    
    if not messages:
        logging.info("No new emails to process.")
        return

    logging.info(f"Found {len(messages)} unread emails (limit: {config.MAX_EMAILS}).")

    # Reverse to process oldest first, so newest ends up at the top Row 2
    messages.reverse()
    new_processed_count = 0
    
    for msg in messages:
        msg_id = msg['id']
        if msg_id in processed_ids:
            continue

        try:
            full_msg = get_email_details(gmail_service, msg_id)
            if not full_msg:
                continue
                
            email_data = parse_email(full_msg)
            
            if config.EMAIL_SUBJECT_FILTER:
                if config.EMAIL_SUBJECT_FILTER.lower() not in email_data['Subject'].lower():
                    logging.info(f"Filtered email: {email_data['Subject']}")
                    processed_ids.add(msg_id)
                    save_processed_ids(processed_ids)
                    continue

            logging.info(f"Processing: {email_data['Subject']}")
            
            row = [
                email_data['From'],
                email_data['Subject'],
                email_data['Date'],
                email_data['Content']
            ]
            
            if prepend_to_sheet(sheets_service, row):
                mark_email_as_read(gmail_service, msg_id)
                processed_ids.add(msg_id)
                new_processed_count += 1
                save_processed_ids(processed_ids)
            else:
                logging.error(f"Failed to prepend {msg_id}")
                
        except Exception as e:
            logging.error(f"Error processing {msg_id}: {e}")

    try:
        trim_sheet(sheets_service, config.MAX_EMAILS)
    except Exception as e:
        logging.error(f"Trim failed: {e}")

    logging.info(f"Batch complete. Processed {new_processed_count} emails.")

if __name__ == '__main__':
    main()
