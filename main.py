import os
import json
import logging
import gcal
import calendar_cleaner
import util
import wtt
from telegram_bot import send_telegram_message
from log_config import setup_logging

logger = setup_logging()

# Load config file
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Support both 'scrape_urls' (new) and 'scrape_url' (legacy single-URL)
if 'scrape_urls' in config:
    scrape_urls = config['scrape_urls']
elif 'scrape_url' in config:
    scrape_urls = [config['scrape_url']]
else:
    raise ValueError('config.json must contain "scrape_urls" (array) or "scrape_url" (string)')

SHARED_CALENDAR_ID = os.getenv('SHARED_CALENDAR_ID')
output_ics = 'purged/calendar.ics'

logger.info('Loaded config with %d URL(s) and %d exclusion(s)',
            len(scrape_urls), len(config['excluded_groups']))
logger.debug('URLs: %s', scrape_urls)
logger.debug('Excluded groups: %s', config['excluded_groups'])

try:
   logger.info('Downloading %d timetable(s)...', len(scrape_urls))
   downloaded_files = wtt.download_all_icals(scrape_urls)

   logger.info('Merging and purging calendars...')
   calendar_cleaner.merge_and_clean_ics_files(downloaded_files, output_ics, config['excluded_groups'])

   logger.info('Checking if calendar changed...')
   calHash = util.compute_file_hash(output_ics)
   oldHash = util.read_hash('hash/calHash')
   if oldHash == '':
      logger.warning('No previous calendar hash found')
      send_telegram_message('No previous calendar hash found')

   if calHash != oldHash:
      logger.info('Calendar hash mismatch — updating')
      logger.debug('Old hash: %s, New hash: %s', oldHash, calHash)
      send_telegram_message('😨 Calendar change detected')
      util.remove_file('hash/calHash.txt')
      util.save_hash(calHash, 'hash/calHash')
      service = gcal.authenticate_google_service()
      gcal.delete_all_events(calendar_id=SHARED_CALENDAR_ID, service=service)
      gcal.upload_to_google_calendar(service, output_ics, calendar_id=SHARED_CALENDAR_ID, subject_color_map=config['subject_color_map'])
      send_telegram_message('✅ Calendar updated successfully!')
      logger.info('Calendar sync complete')
   else:
      logger.info('Calendar unchanged — skipping sync')
      send_telegram_message('😻 No calendar changes detected')

   # Clean up all downloaded and processed files
   for f in downloaded_files:
      if os.path.exists(f):
         os.remove(f)
   if os.path.exists(output_ics):
      os.remove(output_ics)
   logger.debug('Temporary files cleaned up')
except Exception as e:
   logger.exception('Fatal error during sync: %s', e)
   send_telegram_message(f'😭 Something went wrong. {e}')