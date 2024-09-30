import requests
import json
import datetime
import os
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Lade die Konfigurationsdatei
with open('config.json') as config_file:
    config = json.load(config_file)

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Authenticate and create the service
def authenticate_google():
    creds = None
    if os.path.exists(config['token_file']):
        creds = Credentials.from_authorized_user_file(config['token_file'], SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config['client_secret_file'], SCOPES)
            creds = flow.run_local_server(port=0)
        with open(config['token_file'], 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

service = authenticate_google()

def fetch_and_update_calendar():
    # Hole das aktuelle Datum
    heute = datetime.date.today()

    # Überprüfe, ob es Sonntag ist (Sonntag = 6)
    if heute.weekday() == 6:
        heute += datetime.timedelta(days=1)

    # Setze die URL mit dem berechneten Datum
    url = config['url_template'].format(date=heute.strftime('%Y-%m-%d'))

    headers = config['headers']
    cookies = config['cookies']

    response = requests.get(url, headers=headers, cookies=cookies)
    data = response.json()

    # Extract lesson details
    lessons = data['data']['result']['data']['elementPeriods']['4559']
    subject_ids = {
        'WPM_CyberAware': 3243,
        'IT-GRC': 148,
        'MobFor': 150,
        'IT-Sicherheitsmanagement': 149
    }

    for lesson in lessons:
        for element in lesson['elements']:
            if element['id'] in subject_ids.values():
                subject_name = [name for name, id in subject_ids.items() if id == element['id']][0]
                date = datetime.datetime.strptime(str(lesson['date']), '%Y%m%d').date()
                
                # Correctly parse start and end times
                start_hour = int(str(lesson['startTime'])[:-2])
                start_minute = int(str(lesson['startTime'])[-2:])
                end_hour = int(str(lesson['endTime'])[:-2])
                end_minute = int(str(lesson['endTime'])[-2:])
                
                start_time = datetime.datetime.combine(date, datetime.time(start_hour, start_minute)).isoformat()
                end_time = datetime.datetime.combine(date, datetime.time(end_hour, end_minute)).isoformat()

                # Unique identifier for the event
                event_id = f"{subject_name}-{lesson['date']}-{lesson['startTime']}-{lesson['endTime']}"

                # Search for existing events with the same identifier
                events_result = service.events().list(calendarId='primary', q=event_id).execute()
                events = events_result.get('items', [])

                if lesson.get('cellState') == 'CANCEL':
                    if events:
                        for event in events:
                            service.events().delete(calendarId='primary', eventId=event['id']).execute()
                            print(f"Event deleted: {event_id}")
                    else:
                        print(f"No event found to delete: {event_id}")
                else:
                    if not events:
                        event = {
                            'summary': subject_name,
                            'description': event_id,
                            'start': {
                                'dateTime': start_time,
                                'timeZone': 'Europe/Berlin',
                            },
                            'end': {
                                'dateTime': end_time,
                                'timeZone': 'Europe/Berlin',
                            },
                        }

                        event = service.events().insert(calendarId='primary', body=event).execute()
                        print(f"Event created: {event.get('htmlLink')}")
                    else:
                        print(f"Event already exists: {event_id}")

# Main loop to run the script every 30 minutes from 06:00 to 22:00
while True:
    current_time = datetime.datetime.now().time()
    if current_time >= datetime.time(6, 0) and current_time <= datetime.time(22, 0):
        fetch_and_update_calendar()
    time.sleep(1800)  # Sleep for 30 minutes