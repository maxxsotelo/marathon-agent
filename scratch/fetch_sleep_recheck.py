"""
fetch_sleep_recheck.py
Re-fetches sleep data for July 29 after user manually corrected the wake time.
"""
import os, sys
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date(2026, 7, 29).isoformat()

print(f"=== UPDATED SLEEP FOR {today} ===")
try:
    sleep = client.get_sleep_data(today)
    daily_sleep = sleep.get('dailySleepDTO', {})
    
    sleep_score = daily_sleep.get('sleepScores', {}).get('overall', {}).get('value', 'N/A')
    duration_seconds = daily_sleep.get('sleepTimeSeconds', 0)
    duration_hours = duration_seconds / 3600.0
    
    start_time = daily_sleep.get('sleepStartTimestampGMT', 'Unknown')
    end_time = daily_sleep.get('sleepEndTimestampGMT', 'Unknown')
    
    print(f"Sleep Score: {sleep_score}")
    print(f"Duration: {duration_hours:.2f} hours")
    print(f"Raw Start/End GMT: {start_time} to {end_time}")
except Exception as e:
    print(f"Failed to fetch updated sleep: {e}")
