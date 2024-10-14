from ics import Calendar, Event
import requests
import json
import datetime
import pytz

# Lade die Konfigurationsdatei
with open('config.json') as config_file:
    config = json.load(config_file)

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

    calendar = Calendar()

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
                
                # Set timezone to Europe/Berlin
                tz = pytz.timezone('Europe/Berlin')
                start_time = tz.localize(datetime.datetime.combine(date, datetime.time(start_hour, start_minute)))
                end_time = tz.localize(datetime.datetime.combine(date, datetime.time(end_hour, end_minute)))

                # Unique identifier for the event
                event_id = f"{subject_name}-{lesson['date']}-{lesson['startTime']}-{lesson['endTime']}"

                if lesson.get('cellState') != 'CANCEL':
                    event = Event()
                    event.name = subject_name
                    event.begin = start_time
                    event.end = end_time
                    event.description = event_id
                    event.uid = event_id

                    calendar.events.add(event)
                    print(f"Event created: {event_id}")

    with open('calendar.ics', 'w') as f:
        f.writelines(calendar)
        print("ICS file created: calendar.ics")

# Execute the function once
fetch_and_update_calendar()