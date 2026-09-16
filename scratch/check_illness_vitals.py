import os
from datetime import date
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(
    email=os.getenv("GARMIN_EMAIL"),
    password=os.getenv("GARMIN_PASSWORD"),
    prompt_mfa=lambda: input("MFA: "),
)
client.login(TOKEN_STORE)

today = date.today()
print(f"Date: {today}")

summary = client.get_user_summary(today.isoformat())
print(f"  RHR:          {summary.get('restingHeartRate')} bpm")
print(f"  Body Battery: {summary.get('bodyBatteryMostRecentValue')} (High: {summary.get('bodyBatteryHighestValue')}, Low: {summary.get('bodyBatteryLowestValue')})")
print(f"  Stress Avg:   {summary.get('averageStressLevel')}")

hrv = client.get_hrv_data(today.isoformat())
if hrv and "hrvSummary" in hrv:
    s = hrv["hrvSummary"]
    print(f"  HRV Status:   {s.get('status')}")
    print(f"  HRV Last Night: {s.get('lastNightAvg')} ms (5m Peak: {s.get('lastNight5MinHigh')} ms)")
    print(f"  HRV Weekly:   {s.get('weeklyAvg')} ms")

sleep = client.get_sleep_data(today.isoformat())
if sleep and "dailySleepDTO" in sleep:
    dto = sleep["dailySleepDTO"]
    sec = dto.get("sleepTimeSeconds", 0)
    print(f"  Sleep:        {sec/3600:.1f} hrs ({sec//60} mins) | Score: {dto.get('sleepScores', {}).get('overall', {}).get('value')}")
