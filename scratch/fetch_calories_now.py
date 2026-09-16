"""
fetch_calories_now.py
Fetches the absolute latest caloric burn for today to reconcile with the user's watch.
"""
import os, sys
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date(2026, 7, 28).isoformat()

print(f"=== LATEST CALORIES FOR {today} ===")
try:
    stats = client.get_stats(today)
    active = stats.get('activeKilocalories', 0)
    bmr = stats.get('bmrKilocalories', 0)
    total = stats.get('totalKilocalories', 0)
    
    print(f"Via get_stats():")
    print(f"  Active: {active}")
    print(f"  BMR:    {bmr}")
    print(f"  Total:  {total}")
except Exception as e:
    print(f"Error getting stats: {e}")

try:
    summary = client.get_user_summary(today)
    active = summary.get('activeKilocalories', 0)
    bmr = summary.get('bmrKilocalories', 0)
    total = summary.get('totalKilocalories', active + bmr)
    consumed = summary.get('consumedKilocalories', 0)
    
    print(f"\nVia get_user_summary():")
    print(f"  Active: {active}")
    print(f"  BMR:    {bmr}")
    print(f"  Total:  {total}")
    print(f"  Intake: {consumed}")
except Exception as e:
    print(f"Error getting summary: {e}")
