"""
fetch_calories.py
Fetches daily caloric burn for the week of Jul 20 to Jul 26
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

end_date = date(2026, 7, 26)
start_date = end_date - timedelta(days=6)

print("=== WEEKLY CALORIC BURN (Jul 20 - Jul 26) ===")
total_active = 0
total_bmr = 0

current_date = start_date
while current_date <= end_date:
    try:
        stats = client.get_stats(current_date.isoformat())
        # stats is a dict with 'totalKilocalories', 'activeKilocalories', 'bmrKilocalories'
        # in some garminconnect versions it's get_stats_and_body
        active = stats.get('activeKilocalories', 0)
        bmr = stats.get('bmrKilocalories', 0)
        total = stats.get('totalKilocalories', 0)
        
        # fallback if not in get_stats
        if total == 0:
            summary = client.get_user_summary(current_date.isoformat())
            active = summary.get('activeKilocalories', 0)
            bmr = summary.get('bmrKilocalories', 0)
            total = summary.get('totalKilocalories', 0)
            
        print(f"{current_date.strftime('%a, %b %d')}: Total = {total} kcal (Active: {active} | BMR: {bmr})")
        total_active += active
        total_bmr += bmr
    except Exception as e:
        print(f"{current_date.strftime('%a, %b %d')}: Error fetching data - {e}")
    
    current_date += timedelta(days=1)

print("-" * 50)
print(f"WEEKLY TOTAL ACTIVE: {total_active} kcal")
print(f"WEEKLY TOTAL BMR:    {total_bmr} kcal")
print(f"GRAND TOTAL BURN:    {total_active + total_bmr} kcal")
print(f"DAILY AVERAGE:       {(total_active + total_bmr) / 7:.0f} kcal/day")
