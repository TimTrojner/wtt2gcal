# Google Calendar Wise Timetables Sync

Sync your school timetable with Google Calendar and get Telegram notifications!
📝 Why?

I hated the school timetables app, so I created a script that: 

✅ Automatically syncs my school timetable to Google Calendar

✅ Sends updates to a Telegram channel whenever there are changes

✅ Deletes old events to keep the calendar clean

Now, I never have to check the awful timetable app again. 🎉

## ⚙️ Features

✔️ Syncs .ics timetable files to Google Calendar

✔️ Removes old events before syncing

✔️ Notifies a Telegram channel if changes occur

✔️ Filters out unwanted events (e.g., Erasmus, RV1)

✔️ Color-codes events based on subjects

## 🚀 How It Works

1. Downloads `.ics` files from one or more school timetable URLs
2. Merges and cleans the files, removing specific events (e.g., Erasmus, RV1)
3. Checks for changes in the combined timetable
4. Deletes old events from Google Calendar
5. Uploads new events to Google Calendar
6. Sends a Telegram notification if a change is detected

## 🛠️ Setup
### 1️⃣ Install Requirements

It is recommended to use a virtual environment. You can use conda or venv:

**Using Conda:**
```bash
conda create --name urnik python=3.12
conda activate urnik
pip install -r requirements.txt
```

**Using venv:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Set Up Google Calendar API

    Create a Google Cloud Project and enable the Google Calendar API
    Generate a service account JSON key
    Share your Google Calendar with the service account email
    Place the service_account.json file in the project folder

### 3️⃣ Set Up Telegram Bot

    Create a bot with @BotFather
    Get the bot API Token
    Create a Telegram Channel
    Add the bot as an Admin
    Get the Channel ID

### 4️⃣ Create a .env File

Create a .env file in the project folder:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
SHARED_CALENDAR_ID=your_shared_calendar_id
GECKODRIVER_PATH=/path/to/your/geckodriver
LOG_LEVEL=INFO
```

**Notes**:
- If `GECKODRIVER_PATH` is not set, it will default to `geckodriver` (assumes it's in your PATH).
- `LOG_LEVEL` controls logging verbosity. Valid values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Defaults to `INFO`.

### 5️⃣ Configure config.json

Create or edit `config.json` in the project folder to customize your setup:

```json
{
  "scrape_urls": [
    "https://www.wise-tt.com/wtt_um_feri/index.jsp?filterId=0;254,538;0;0;",
    "https://www.wise-tt.com/wtt_um_feri/index.jsp?filterId=0;254,539;0;0;"
  ],
  "excluded_groups": [
    "RV1",
    "Erasmus"
  ],
  "subject_color_map": {
    "INTELIGENTNI SISTEMI": "11",
    "RAČUNALNIŠKA OBDELAVA SIGNALOV IN SLIK": "9",
    "POVEZLJIVI SISTEMI IN INTELIGENTNE STORITVE": "6",
    "JEZIKOVNE TEHNOLOGIJE": "5",
    "IZBRANI ALGORITMI KOMBINATORIKE": "8"
  }
}
```

- **scrape_urls**: Array of URLs to scrape timetables from (events are merged into a single calendar)
- **excluded_groups**: Array of strings - events containing any of these in the description will be filtered out (applied across all URLs)
- **subject_color_map**: Map of subject names to Google Calendar color IDs (1-11)

### ▶️ Usage

Run the sync script manually:

`python main.py`

Or set up a cron job for automatic updates:

`0 1 * * * /bin/bash -c 'source /root/miniconda3/bin/activate urnik && python /root/urnik/main.py >> /root/urnik/job_log.txt 2>&1 && conda deactivate'`



## 📌 Configuration

You can customize the behavior through `config.json`:

- **scrape_urls**: Add one or more timetable URLs. Events from all URLs are merged into a single calendar before syncing.
- **excluded_groups**: Add or remove group identifiers (e.g., "RV1", "RV2", "Erasmus") to filter out unwanted events. Exclusions apply across all URLs.
- **subject_color_map**: Customize colors for different subjects using Google Calendar color IDs (1-11)

Example: To exclude RV2 instead of RV1, simply change `"RV1"` to `"RV2"` in the excluded_groups array.

> **Note**: The legacy `scrape_url` (single string) is still supported for backward compatibility.

