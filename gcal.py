import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from icalendar import Calendar

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'service_account.json'

def get_event_color(summary, subject_color_map=None):
    """Determine the event color based on subject."""
    if subject_color_map is None:
        subject_color_map = {}
    
    for subject, color_id in subject_color_map.items():
        if subject.lower() in summary.lower():
            return color_id
    return '1'

def authenticate_google_service():
    """Authenticate using a Google Service Account."""
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

def list_calendars(service):
    calendars = service.calendarList().list().execute()
    for calendar in calendars['items']:
        print(f'Name: {calendar['summary']}, ID: {calendar['id']}')

def upload_to_google_calendar(service, ics_file, calendar_id, subject_color_map=None):
    """Upload events from .ics to Google Calendar."""

    with open(ics_file, 'r', encoding='utf-8') as f:
        calendar = Calendar.from_ical(f.read())

    cal_len = len(calendar.walk())
    events_added = 0

    for component in calendar.walk():
        if component.name == 'VEVENT':
            summary = component.get('SUMMARY', 'No Title')
            color_id = get_event_color(summary, subject_color_map)

            event = {
                'summary': summary,
                'location': component.get('LOCATION'),
                'description': component.get('DESCRIPTION'),
                'start': {
                    'dateTime': component.get('DTSTART').dt.isoformat(),
                    'timeZone': 'Europe/Ljubljana',
                },
                'end': {
                    'dateTime': component.get('DTEND').dt.isoformat(),
                    'timeZone': 'Europe/Ljubljana',
                },
                'colorId': color_id,
            }

            service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f'Added event: {event.get('summary', 'No Title')} (ID: {event.get('id')})')
            events_added += 1
            print(f'Added {events_added} of {cal_len} events')
            time.sleep(.5)

    print('Events uploaded successfully.')

def add_shared_calendar(shared_calendar_id, service):
    """Manually add a shared calendar to the service account's calendar list."""

    calendar_list_entry = {
        'id': shared_calendar_id
    }

    service.calendarList().insert(body=calendar_list_entry).execute()
    print(f'Shared calendar {shared_calendar_id} added successfully!')

def delete_all_events(calendar_id, service):
    events_result = service.events().list(
        calendarId=calendar_id,
        singleEvents=True  # Ensure recurring events are expanded
    ).execute()

    events = events_result.get('items', [])
    events_length = len(events)
    num_of_deleted_events = 0

    if not events:
        print('No events found')
        return

    for event in events:
        event_id = event['id']
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print(f'Deleted event: {event.get('summary', 'No Title')} (ID: {event_id})')
        num_of_deleted_events += 1
        print(f'Deleted {num_of_deleted_events} of {events_length} events')
        time.sleep(.5)

    print('✅ All events deleted successfully.')


# need to be owner rip - working with service account
def clear_calendar(calendar_id, service):
    """Wipes all events from the calendar instantly (irreversible)."""
    service.calendars().clear(calendarId=calendar_id).execute()
    print('✅ Calendar cleared successfully!')

def list_events(service, calendar_id):
    """List events from a Google Calendar ID."""
    events_result = service.events().list(
        calendarId=calendar_id,
        singleEvents=True
    ).execute()
    print('Raw events response:', events_result)
    events = events_result.get('items', [])
    if not events:
        print('No events found.')
        return
