import os
import json
from garminconnect import Garmin
from datetime import date, timedelta

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
try:
    client.login(TOKEN_STORE)
except Exception as e:
    print("Login failed:", e)
    exit(1)

today = date.today().isoformat()
acts = client.get_activities_by_date(today, (date.today() + timedelta(days=1)).isoformat())

print(f"Activities on {today}:")
for a in acts:
    if a.get("activityType", {}).get("typeKey") == "running":
        dist = (a.get("distance") or 0) / 1000
        print(f"ID: {a['activityId']} | Distance: {dist:.2f} km | Name: {a.get('activityName')}")
