import os
import json
from datetime import date
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date.today().isoformat()

print(f"--- Vitals for {today} ---")
try:
    sleep = client.get_sleep_data(today)
    print("Sleep Score:", sleep.get("dailySleepDTO", {}).get("sleepScore", "N/A"))
    print("Resting HR:", sleep.get("dailySleepDTO", {}).get("restingHeartRate", "N/A"))
except Exception as e:
    print("Sleep:", e)

try:
    hrv = client.get_hrv_data(today)
    print("HRV 7d Avg:", hrv.get("hrvSummary", {}).get("weeklyAvg", "N/A"))
    print("HRV Last Night:", hrv.get("hrvSummary", {}).get("lastNightAvg", "N/A"))
except Exception as e:
    print("HRV:", e)
