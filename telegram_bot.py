import os
import logging

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('urnik.telegram')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

def send_telegram_message(message):
    """Send a message to a Telegram channel."""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': message
    }
    response = requests.post(url, data=data)
    result = response.json()
    if result.get('ok'):
        logger.debug('Telegram message sent: %s', message)
    else:
        logger.error('Telegram send failed: %s', result)
    return result
