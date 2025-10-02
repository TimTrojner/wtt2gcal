import gcal
import os
from dotenv import load_dotenv

load_dotenv()

service = gcal.authenticate_google_service()
SHARED_CALENDAR_ID = os.getenv('SHARED_CALENDAR_ID')
gcal.delete_all_events(calendar_id=SHARED_CALENDAR_ID, service=service)
