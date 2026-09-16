"""
audit_mileage.py
"""
import os, sys
from datetime import date, timedelta
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

# Get today
today = date(2026, 8, 12)
start_date = today - timedelta(days=60) # last 8 weeks roughly

activities = client.get_activities_by_date(start_date.isoformat(), today.isoformat())

run_types = ("running", "treadmill_running", "trail_running")

print("Historical activities fetched.")
