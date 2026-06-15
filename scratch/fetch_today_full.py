import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = "2026-05-27"

# --- Vitals ---
print("=== VITALS (May 27) ===")
try:
    summary = client.get_user_summary(today)
    print(f"Body Battery:    {summary.get('bodyBatteryMostRecentValue')}")
    print(f"Resting HR:      {summary.get('restingHeartRate')}")
    print(f"Stress Score:    {summary.get('averageStressLevel')}")
    print(f"Steps:           {summary.get('totalSteps')}")
    print(f"Intensity Min:   Moderate {summary.get('moderateIntensityMinutes', 0)}m | Vigorous {summary.get('vigorousIntensityMinutes', 0)}m")
except Exception as e:
    print(f"Summary error: {e}")

# --- HRV ---
print("\n=== HRV ===")
try:
    hrv = client.get_hrv_data(today)
    hrv_sum = hrv.get("hrvSummary", {})
    print(f"Last Night HRV:  {hrv_sum.get('lastNight')} ms")
    print(f"5-day Avg HRV:   {hrv_sum.get('lastFive')} ms")
    print(f"Weekly Avg HRV:  {hrv_sum.get('weekly')} ms")
    print(f"HRV Status:      {hrv_sum.get('status')}")
except Exception as e:
    print(f"HRV error: {e}")

# --- Sleep ---
print("\n=== SLEEP ===")
try:
    sleep = client.get_sleep_data(today)
    sd = sleep.get("dailySleepDTO", {})
    print(f"Sleep Score:     {sd.get('sleepScores', {}).get('overall', {}).get('value', 'N/A')}")
    print(f"Total Sleep:     {sd.get('sleepTimeSeconds', 0)//3600}h {(sd.get('sleepTimeSeconds', 0)%3600)//60}m")
    print(f"Deep Sleep:      {sd.get('deepSleepSeconds', 0)//60}m")
    print(f"REM Sleep:       {sd.get('remSleepSeconds', 0)//60}m")
    print(f"Light Sleep:     {sd.get('lightSleepSeconds', 0)//60}m")
    print(f"Awake:           {sd.get('awakeSleepSeconds', 0)//60}m")
except Exception as e:
    print(f"Sleep error: {e}")

# --- Today's activities ---
print("\n=== TODAY'S ACTIVITIES ===")
try:
    activities = client.get_activities_by_date(today, today)
    if not activities:
        print("No activities recorded today yet.")
    for act in activities:
        print(f"\nActivity:      {act.get('activityName')}")
        print(f"  Sport:       {act.get('activityType', {}).get('typeKey', 'N/A')}")
        print(f"  Duration:    {act.get('duration', 0)/60:.1f} min")
        print(f"  Distance:    {act.get('distance', 0)/1000:.2f} km")
        print(f"  Avg HR:      {act.get('averageHR')} bpm")
        print(f"  Max HR:      {act.get('maxHR')} bpm")
        print(f"  Avg Power:   {act.get('avgPower')} W")
        print(f"  Calories:    {act.get('calories')} kcal")
        print(f"  Training Effect (Aerobic): {act.get('aerobicTrainingEffect')}")
        print(f"  Training Effect (Anaerobic): {act.get('anaerobicTrainingEffect')}")
except Exception as e:
    print(f"Activities error: {e}")

# --- Recent 5 activities for context ---
print("\n=== RECENT 5 ACTIVITIES (Context) ===")
try:
    recent = client.get_activities(0, 5)
    for act in recent:
        name = act.get('activityName', 'N/A')
        sport = act.get('activityType', {}).get('typeKey', 'N/A')
        dur = act.get('duration', 0)/60
        dist = act.get('distance', 0)/1000
        avg_hr = act.get('averageHR', 'N/A')
        start = act.get('startTimeLocal', 'N/A')
        print(f"  [{start}] {name} ({sport}) — {dur:.0f}min | {dist:.2f}km | HR {avg_hr}")
except Exception as e:
    print(f"Recent activities error: {e}")
