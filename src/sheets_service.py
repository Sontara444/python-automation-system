
from googleapiclient.discovery import build
from tenacity import retry, stop_after_attempt, wait_exponential
import config
from src.gmail_service import get_credentials

def get_sheets_service():
    """Builds and returns the Sheets service."""
    creds = get_credentials()
    return build('sheets', 'v4', credentials=creds)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def append_to_sheet(service, values):
    """Appends a row of values to the configured spreadsheet."""
    try:
        body = {'values': [values]}
        return service.spreadsheets().values().append(
            spreadsheetId=config.SPREADSHEET_ID,
            range=config.RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
    except Exception as e:
        print(f"An error occurred appending to sheet: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def prepend_to_sheet(service, values):
    """Inserts a row of values at the top (Row 2)."""
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=config.SPREADSHEET_ID).execute()
        sheet_id = spreadsheet.get('sheets', [{}])[0].get('properties', {}).get('sheetId', 0)

        requests = [{
            'insertDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': 1,
                    'endIndex': 2
                },
                'inheritFromBefore': False
            }
        }]
        service.spreadsheets().batchUpdate(
            spreadsheetId=config.SPREADSHEET_ID,
            body={'requests': requests}
        ).execute()

        body = {'values': [values]}
        return service.spreadsheets().values().update(
            spreadsheetId=config.SPREADSHEET_ID,
            range='Sheet1!A2',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
    except Exception as e:
        print(f"An error occurred prepending to sheet: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def trim_sheet(service, max_rows):
    """Deletes rows beyond the specified limit (excluding headers)."""
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=config.SPREADSHEET_ID).execute()
        sheet = spreadsheet.get('sheets', [{}])[0]
        sheet_id = sheet.get('properties', {}).get('sheetId', 0)
        grid_properties = sheet.get('properties', {}).get('gridProperties', {})
        total_rows = grid_properties.get('rowCount', 0)

        limit_line = max_rows + 1
        
        if total_rows > limit_line:
            requests = [{
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'ROWS',
                        'startIndex': limit_line,
                        'endIndex': total_rows
                    }
                }
            }]
            service.spreadsheets().batchUpdate(
                spreadsheetId=config.SPREADSHEET_ID,
                body={'requests': requests}
            ).execute()
            print(f"Trimmed sheet to {max_rows} rows.")
    except Exception as e:
        print(f"An error occurred trimming sheet: {e}")
