import requests
import json
import datetime
import os
import time

# Lade die Konfigurationsdatei
with open('config.json') as config_file:
    config = json.load(config_file)

def save_lessons_to_file(lessons, filename):
    with open(filename, 'w') as file:
        json.dump(lessons, file)

def load_lessons_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return []

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{config['telegram_bot_token']}/sendMessage"
    payload = {
        'chat_id': config['telegram_chat_id'],
        'text': message
    }
    requests.post(url, json=payload)

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

    current_lessons = []
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

                lesson_info = {
                    'subject_name': subject_name,
                    'date': str(date),
                    'start_time': start_time,
                    'end_time': end_time,
                    'cell_state': lesson.get('cellState')
                }
                current_lessons.append(lesson_info)

    previous_lessons = load_lessons_from_file('lessons.json')

    for current_lesson in current_lessons:
        if current_lesson['cell_state'] == 'CANCEL':
            if current_lesson not in previous_lessons:
                message = f"Lesson Cancelled: {current_lesson['subject_name']} on {current_lesson['date']} from {current_lesson['start_time']} to {current_lesson['end_time']}"
                send_telegram_message(message)

    save_lessons_to_file(current_lessons, 'lessons.json')

# Main loop to run the script every 30 minutes from 06:00 to 22:00
while True:
    current_time = datetime.datetime.now().time()
    if current_time >= datetime.time(6, 0) and current_time <= datetime.time(22, 0):
        fetch_and_update_calendar()
    time.sleep(1800)  # Sleep for 30 minutes