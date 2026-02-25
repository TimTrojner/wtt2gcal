import time
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from icalendar import Calendar

logger = logging.getLogger('urnik.gcal')

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
    service = build('calendar', 'v3', credentials=creds)
    logger.info('Authenticated with Google Calendar API')
    return service

def list_calendars(service):
    calendars = service.calendarList().list().execute()
    for calendar in calendars['items']:
        logger.info('Calendar: %s (ID: %s)', calendar['summary'], calendar['id'])

def upload_to_google_calendar(service, ics_file, calendar_id, subject_color_map=None):
    """Upload events from .ics to Google Calendar."""

    with open(ics_file, 'r', encoding='utf-8') as f:
        calendar = Calendar.from_ical(f.read())

    # Count VEVENT components only
    total_events = sum(1 for c in calendar.walk() if c.name == 'VEVENT')
    events_added = 0

    logger.info('Uploading %d events to Google Calendar...', total_events)

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
            events_added += 1
            logger.debug('Added event %d/%d: %s', events_added, total_events, summary)
            time.sleep(.5)

    logger.info('Upload complete: %d events added', events_added)

def add_shared_calendar(shared_calendar_id, service):
    """Manually add a shared calendar to the service account's calendar list."""

    calendar_list_entry = {
        'id': shared_calendar_id
    }

    service.calendarList().insert(body=calendar_list_entry).execute()
    logger.info('Shared calendar %s added successfully', shared_calendar_id)

def delete_all_events(calendar_id, service):
    events_result = service.events().list(
        calendarId=calendar_id,
        singleEvents=True  # Ensure recurring events are expanded
    ).execute()

    events = events_result.get('items', [])
    total = len(events)

    if not events:
        logger.info('No events to delete')
        return

    logger.info('Deleting %d events from calendar...', total)
    deleted = 0

    for event in events:
        event_id = event['id']
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        deleted += 1
        logger.debug('Deleted event %d/%d: %s (ID: %s)',
                      deleted, total, event.get('summary', 'No Title'), event_id)
        time.sleep(.5)

    logger.info('Deletion complete: %d events removed', deleted)


# need to be owner rip - working with service account
def clear_calendar(calendar_id, service):
    """Wipes all events from the calendar instantly (irreversible)."""
    service.calendars().clear(calendarId=calendar_id).execute()
    logger.info('Calendar cleared')

def list_events(service, calendar_id):
    """List events from a Google Calendar ID."""
    events_result = service.events().list(
        calendarId=calendar_id,
        singleEvents=True
    ).execute()
    logger.debug('Raw events response: %s', events_result)
    events = events_result.get('items', [])
    if not events:
        logger.info('No events found')
        return
