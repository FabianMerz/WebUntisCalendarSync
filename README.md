# WebUntis to Google Calendar Sync

This repository contains a Python script that fetches timetables from WebUntis and syncs them with Google Calendar. The script periodically sends requests to the WebUntis API to fetch the latest timetables and updates the Google Calendar accordingly.

## Prerequisites

- Python 3.x
- Google API Client Library for Python
- Requests Library

## Installation

1. Clone the repository:

2. Manually install the required Python packages:
    ```sh
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
    ```

3. Create a [`config.json`] file in the same directory as your script and add the following content:

    ```json
    {
        "token_file": "token.json",
        "client_secret_file": "client_secret.json",
        "url_template": "https://example.com/api/timetable?elementType=1&elementId=1234&date={date}&formatId=2",
        "headers": {
            "Host": "example.com",
            "Sec-Ch-Ua": "\"Chromium\";v=\"121\", \"Not A(Brand\";v=\"99\"",
            "Accept": "application/json",
            "Tenant-Id": "1234567",
            "Sec-Ch-Ua-Mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.160 Safari/537.36",
            "Sec-Ch-Ua-Platform": "\"macOS\"",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "-Fetch-Dest": "empty",
            "Referer": "https://example.com/embedded",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Priority": "u=1, i"
        },
        "cookies": {
            "JID": "FAKEJID1234567890",
            "schoolname": "FAKESCHOOL",
            "Tenant-Id": "1234567",
            "traceId": "FAKETRACEID1234567890",
            "_sleek_session": "%7B%22init%22%3A%222024-09-29T17%3A22%3A27.754Z%22%7D",
            "_sleek_product": "%7B%22token%22%3A%22FAKETOKEN1234567890%22%2C%22user_data%22%3A%7B%22user_id%22%3A1234567%2C%22admin_id%22%3A0%2C%22sso%22%3Atrue%2C%22anonymous%22%3Afalse%2C%22data_name%22%3A%22FAKENAME%22%2C%22data_full_name%22%3A%22%22%2C%22data_mail%22%3A%22fake%40example.com%22%2C%22data_img%22%3A%22https%3A%2F%2Fexample.com%2Fstatic%2Fimage%2Fuser.png%22%2C%22segments%22%3A%5B%22fake-segment%22%5D%2C%22notify%22%3A1%2C%22notify_settings%22%3A%7B%22mention%22%3Atrue%2C%22changelog%22%3Afalse%2C%22subscribed%22%3Atrue%7D%7D%7D"
        }
    }
    ```

4. Fetch the course IDs from the WebUntis API response. You can use tools like Burp Suite to intercept the requests and extract the necessary IDs. For example:

    ```python
    # Extract lesson details
    lessons = data['data']['result']['data']['elementPeriods']['4559']
    subject_ids = {
        'WPM_CyberAware': 3243,
        'IT-GRC': 148,
        'MobFor': 150,
        'IT-Sicherheitsmanagement': 149
    }
    ```

## Configuration File ([`config.json`])

The [`config.json`] file contains all the sensitive data and configuration parameters required by the script:

- `token_file`: The path to the file that stores the OAuth 2.0 access tokens.
- `client_secret_file`: The path to the file that contains the client ID and client secret for the Google API.
- `url_template`: The URL template for the WebUntis API request. The `{date}` placeholder will be replaced with the current date.
- `headers`: HTTP headers required for the WebUntis API request. These can be intercepted using tools like Burp Suite.
- `cookies`: HTTP cookies required for the WebUntis API request. These can also be intercepted using tools like Burp Suite.

## Google OAuth 2.0 Authentication

The script uses OAuth 2.0 for authentication with the Google Calendar API. The first time you run the script, you will be prompted to log in via the browser and grant the necessary permissions. The access tokens will be saved in the file specified in `token_file` and used for subsequent runs.

## Running the Script

To run the script, use the following command:

```sh
python3 Kalender.py
```

The script will then periodically send requests to the WebUntis API and update the Google Calendar accordingly.


## Legal Disclaimer

The owner of this repository does not accept any liability for any damages or losses that may arise from the use of this script. Use it at your own risk.