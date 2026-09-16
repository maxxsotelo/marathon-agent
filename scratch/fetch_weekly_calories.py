"""
fetch_weekly_calories.py
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

end_date = date(2026, 8, 8)
start_date = end_date - timedelta(days=6)

print(f"Fetching caloric data from {start_date} to {end_date}...\n")

total_burn = 0
active_burn = 0
days = 0

for i in range(7):
    d = start_date + timedelta(days=i)
    try:
        stats = client.get_user_summary(d.isoformat())
        tkcal = stats.get('totalKilocalories', 0)
        akcal = stats.get('activeKilocalories', 0)
        bkcal = stats.get('bmrKilocalories', 0)
        
        print(f"[{d.isoformat()}] Total: {tkcal} kcal | Active: {akcal} kcal | BMR: {bkcal} kcal")
        
        total_burn += tkcal
        active_burn += akcal
        if tkcal > 0:
            days += 1
    except Exception as e:
        print(f"[{d.isoformat()}] Failed: {e}")

if days > 0:
    print(f"\n=== WEEKLY TOTALS ({days} days) ===")
    print(f"Total Kilocalories Burned: {total_burn}")
    print(f"Average Daily Burn: {total_burn / days:.0f} kcal/day")
    print(f"Total Active Calories: {active_burn} kcal")
