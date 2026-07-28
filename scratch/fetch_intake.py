"""
fetch_intake.py
Fetches daily caloric intake and compares to burn for the week of Jul 20 to Jul 26
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

total_intake = 0
total_burn = 0

current_date = start_date
while current_date <= end_date:
    try:
        stats = client.get_stats(current_date.isoformat())
        burn = stats.get('totalKilocalories', 0)
        
        # fallback
        if burn == 0:
            summary = client.get_user_summary(current_date.isoformat())
            burn = summary.get('totalKilocalories', 0)
            intake = summary.get('consumedKilocalories', 0)
        else:
            intake = stats.get('consumedKilocalories', 0)
            
        print(f"{current_date.strftime('%a, %b %d')}: Burned = {burn} kcal | Consumed = {intake} kcal | Net = {intake - burn} kcal")
        
        total_burn += burn
        if intake: # might be None
            total_intake += intake
            
    except Exception as e:
        print(f"{current_date.strftime('%a, %b %d')}: Error - {e}")
    
    current_date += timedelta(days=1)

print("-" * 50)
print(f"WEEKLY TOTAL BURN:    {total_burn} kcal")
print(f"WEEKLY TOTAL INTAKE:  {total_intake} kcal")
print(f"WEEKLY NET DEFICIT/SURPLUS: {total_intake - total_burn} kcal")
