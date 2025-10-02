import os
import json
import gcal
import calendar_cleaner
import util
import wtt
from telegram_bot import send_telegram_message
from dotenv import load_dotenv

load_dotenv()

# Load config file
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

SHARED_CALENDAR_ID = os.getenv('SHARED_CALENDAR_ID')
input_ics = 'downloads/calendar.ics'
output_ics = 'purged/calendar.ics'

try:
   print('Downloading calendar...')
   driver, wait = wtt.init_driver()
   driver.get(config['scrape_url'])
   downloaded_files = wtt.download_ical(wait)

   print('Purging calendar...')
   calendar_cleaner.clean_ics_file(input_ics, output_ics, config['excluded_groups'])

   print('Checking if calendar changed')
   calHash = util.compute_file_hash('purged/calendar.ics')
   oldHash = util.read_hash('hash/calHash')
   if oldHash == '':
      print('No previous calendar hash found')
      send_telegram_message('No previous calendar hash found')

   if calHash != oldHash:
      print('Calendar hash mismatch')
      send_telegram_message('😨 Calendar change detected')
      util.remove_file('hash/calHash.txt')
      util.save_hash(calHash, 'hash/calHash')
      service = gcal.authenticate_google_service()
      gcal.delete_all_events(calendar_id=SHARED_CALENDAR_ID, service=service)
      gcal.upload_to_google_calendar(service, output_ics, calendar_id=SHARED_CALENDAR_ID, subject_color_map=config['subject_color_map'])
      send_telegram_message('✅ Calendar updated successfully!')
   else:
      print('Calendar is the same')
      send_telegram_message('😻 No calendar changes detected')

   os.remove(input_ics)
   os.remove(output_ics)
except Exception as e:
   print(e)
   send_telegram_message(f'😭 Something went wrong. {e}')