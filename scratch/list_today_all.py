import os
from garminconnect import Garmin
from datetime import date, timedelta

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

start = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
end = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
acts = client.get_activities_by_date(start, end)
for a in acts:
    date_str = a.get("startTimeLocal", "")
    name = a.get("activityName", "Unknown")
    type_ = a.get("activityType", {}).get("typeKey", "unknown")
    dur = a.get("duration", 0) / 60
    hr = a.get("averageHR", 0)
    print(f"[{date_str}] [{type_}] {name} - {dur:.1f} min - Avg HR: {hr}")
