import os
import json
from garminconnect import Garmin
from datetime import date, timedelta, datetime

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
try:
    client.login(TOKEN_STORE)
except Exception as e:
    print("Login failed:", e)
    exit(1)

today = date.today()
acts = client.get_activities_by_date(
    (today - timedelta(days=14)).strftime("%Y-%m-%d"),
    today.strftime("%Y-%m-%d"),
    "running"
)

acute_start  = today - timedelta(days=7) # Wait, is it 7 days or 6 days? today - 7
print(f"Acute Start Date: {acute_start}")

acute_km = 0.0
for act in sorted(acts, key=lambda x: x["startTimeLocal"]):
    dt = datetime.strptime(act["startTimeLocal"], "%Y-%m-%d %H:%M:%S").date()
    km = (act.get("distance") or 0) / 1000
    print(f"{dt} | {km:.2f} km | {act.get('activityName')}")
    if dt >= acute_start:
        acute_km += km

print(f"Total Acute (from {acute_start}): {acute_km:.2f} km")
