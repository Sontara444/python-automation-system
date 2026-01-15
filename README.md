# Gmail to Google Sheets Automation

## Project Overview
This project is a Python automation system that reads unread emails from a Gmail account
using the Gmail API and saves them into a Google Sheet using the Google Sheets API.

Each email is stored with the following details:
- From: Sender email address
- Subject: Email subject
- Date: Date and time received
- Content: Email body in plain text

The project uses OAuth 2.0 authentication and prevents duplicate entries.

---

## High-Level Architecture
Gmail Inbox (Unread Emails)
        |
        | Gmail API (OAuth 2.0)
        |
Python Script
        |
        |-- Fetch unread emails
        |-- Parse email data
        |-- Save to Google Sheets
        |
Google Sheet
        |
state.json (stores processed email IDs)

---

## Project Structure

gmail-to-sheets/
├── src/
│   ├── gmail_service.py
│   ├── sheets_service.py
│   ├── email_parser.py
│   └── main.py
├── credentials/
│   └── credentials.json (DO NOT COMMIT)
├── proof/
│   ├── gmail_unread_inbox.png
│   ├── google_sheet_rows.png
│   └── oauth_consent_screen.png
├── state.json
├── config.py
├── requirements.txt
├── .gitignore
└── README.md

---

## Setup Instructions

1. Clone the repository
   git clone <repository-url>
   cd gmail-to-sheets

2. Create and activate virtual environment
   python -m venv venv
   Windows: .\venv\Scripts\Activate.ps1

3. Install dependencies
   pip install -r requirements.txt

4. Google Cloud setup
   - Enable Gmail API
   - Enable Google Sheets API
   - Configure OAuth consent screen
   - Create OAuth Desktop credentials
   - Download credentials.json
   - Place it inside credentials/ folder

5. Configure Google Sheet
   - Create a Google Sheet with headers:
     From | Subject | Date | Content
   - Copy Spreadsheet ID
   - Add it in config.py

6. Run the project
   python src/main.py

---

## Bonus Features

- Subject-based filtering to process only required emails
- Retry logic with exponential backoff for Gmail and Sheets API calls
- Logging with timestamps for better debugging
- Limit of 10 most recent unread emails per run

---

## OAuth Flow Used
The project uses OAuth 2.0 Desktop Application flow.
On first run, a browser opens for Google login.
After approval, access and refresh tokens are saved locally.
Next runs use the saved token automatically.

---

## Duplicate Prevention Logic
Each email has a unique message ID.
After processing an email, its ID is stored in state.json.
Before processing a new email, the script checks state.json.
If the ID already exists, the email is skipped.
This prevents duplicate rows in Google Sheets.

---

## State Persistence Method
Processed email IDs are stored in a local file called state.json.
This file is reused on every run.
This approach is simple, reliable, and does not require a database.

---

## Challenge Faced
OAuth access was blocked during testing.
This happened because the app was in testing mode.
The issue was fixed by adding the Gmail account as a test user
in the OAuth consent screen settings.

---

## Limitations
- Only unread emails are processed
- Email content is stored as plain text
- Uses local state.json file
- Script runs manually

---

## Proof of Execution
Screenshots are available in the proof folder:
- Gmail inbox with unread emails
- Google Sheet with at least 5 rows
- OAuth consent screen

---

## Demo Video
Video link:
https://drive.google.com/file/d/1rfdR3PTnv6J8HWDF7A542rx4LVYes_ou/view?usp=sharing

---

## Security
- credentials.json is not committed
- OAuth tokens are ignored using .gitignore
- No API keys are exposed

---

## Author
Sontara 
