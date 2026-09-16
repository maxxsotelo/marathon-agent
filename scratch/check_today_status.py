import os
from datetime import date, timedelta
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

# Yesterday and today's activities
acts = client.get_activities_by_date((today - timedelta(days=2)).isoformat(), today.isoformat())
print(f"\nActivities in last 2 days ({len(acts)}):")
for a in acts:
    t = a.get("activityType", {}).get("typeKey", "?")
    name = a.get("activityName", "?")
    d = a.get("startTimeLocal", "?")
    dist = (a.get("distance") or 0) / 1000
    dur = (a.get("duration") or 0) / 60
    ahr = a.get("averageHR", "-")
    mhr = a.get("maxHR", "-")
    ae = a.get("aerobicTrainingEffect", "-")
    an = a.get("anaerobicTrainingEffect", "-")
    print(f"  {d} | {t:18s} | {dist:5.2f}km | {dur:4.1f}min | HR: {ahr}/{mhr} | TE: Ae{ae}/An{an} | {name}")

# Overnight HRV & sleep
print("\nOvernight Vitals:")
hrv = client.get_hrv_data(today.isoformat())
if hrv and "hrvSummary" in hrv:
    s = hrv["hrvSummary"]
    print(f"  HRV Status:         {s.get('status')}")
    print(f"  HRV Weekly Avg:     {s.get('weeklyAvg')} ms")
    print(f"  HRV Last Night:     {s.get('lastNightAvg')} ms (5m peak: {s.get('lastNight5MinHigh')} ms)")
    print(f"  HRV Baseline:       {s.get('baselineBalancedLow')} - {s.get('baselineBalancedUpper')} ms")

sleep = client.get_sleep_data(today.isoformat())
if sleep and "dailySleepDTO" in sleep:
    dto = sleep["dailySleepDTO"]
    sec = dto.get("sleepTimeSeconds", 0)
    print(f"  Sleep Duration:     {sec/3600:.1f} hrs ({sec//60} mins) | Score: {dto.get('sleepScores', {}).get('overall', {}).get('value')}")

summary = client.get_user_summary(today.isoformat())
print(f"  RHR:                {summary.get('restingHeartRate')} bpm")
print(f"  Body Battery:       {summary.get('bodyBatteryMostRecentValue')} (High: {summary.get('bodyBatteryHighestValue')}, Low: {summary.get('bodyBatteryLowestValue')})")
print(f"  Stress Avg:         {summary.get('averageStressLevel')}")
