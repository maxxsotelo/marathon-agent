import os, sys
from dotenv import load_dotenv
from garminconnect import Garmin
from datetime import date, timedelta

load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(os.path.expanduser("~/.garminconnect"))

end = date.today()
start = end - timedelta(days=21)
activities = client.get_activities_by_date(start.isoformat(), end.isoformat())

print("=== PAST STRENGTH SESSIONS ===")
for act in activities:
    if act.get("activityType", {}).get("typeKey") == "strength_training":
        date_str = act.get("startTimeLocal", "")[:10]
        print(f"{date_str} | ID: {act.get('activityId')} | Name: {act.get('activityName')}")
