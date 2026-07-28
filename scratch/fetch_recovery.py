import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date.today().isoformat()
stats = client.get_stats(today)
print("=== TODAY'S RECOVERY SNAPSHOT ===")
print(f"Body Battery (current): {stats.get('bodyBatteryMostRecentValue')}")
print(f"Training Load (7d):     {stats.get('trainingLoad')}")
print(f"Acute Training Load:    {stats.get('acuteTrainingLoad')}")
print(f"Chronic Training Load:  {stats.get('chronicTrainingLoad')}")
print(f"Training Status:        {stats.get('trainingStatus')}")
print(f"Recovery Time (hrs):    {stats.get('recoveryTime')}")

print()
print("=== TODAY'S ACTIVITIES RECOVERY ===")
acts = client.get_activities_by_date("2026-07-04", "2026-07-04")
for a in acts:
    name = a.get("activityName", "")
    sport = a.get("activityType", {}).get("typeKey", "")
    rec = a.get("recoveryTime")
    load = a.get("activityTrainingLoad")
    aer_te = a.get("aerobicTrainingEffect")
    print(f"{name}: Recovery={rec}h | Load={load} | Aer TE={aer_te}")
