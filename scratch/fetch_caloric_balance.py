"""
fetch_caloric_balance.py
Fetches daily caloric burn vs intake for the last 7 days.
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

end_date = date(2026, 7, 28)
start_date = end_date - timedelta(days=6)

print(f"=== CALORIC BALANCE ({start_date} to {end_date}) ===")
total_burn = 0
total_intake = 0
days_tracked = 0

current_date = start_date
while current_date <= end_date:
    try:
        summary = client.get_user_summary(current_date.isoformat())
        active = summary.get('activeKilocalories', 0)
        bmr = summary.get('bmrKilocalories', 0)
        total_b = summary.get('totalKilocalories', active + bmr)
        
        # Consumed via MyFitnessPal integration
        consumed = summary.get('consumedKilocalories', 0)
        
        balance = consumed - total_b
        bal_str = f"+{balance}" if balance > 0 else str(balance)
        
        print(f"{current_date.strftime('%a, %b %d')}: Burned {total_b} kcal | Consumed {consumed} kcal | Net: {bal_str}")
        
        total_burn += total_b
        if consumed > 0:
            total_intake += consumed
            days_tracked += 1
            
    except Exception as e:
        print(f"{current_date.strftime('%a, %b %d')}: Error fetching data - {e}")
    
    current_date += timedelta(days=1)

print("-" * 50)
if days_tracked > 0:
    print(f"Total Burned (7d):    {total_burn} kcal (Avg {total_burn/7:.0f}/day)")
    print(f"Total Consumed (7d):  {total_intake} kcal (Avg {total_intake/days_tracked:.0f}/day over {days_tracked} tracked days)")
    net = total_intake - total_burn
    print(f"NET BALANCE:          {'+' if net > 0 else ''}{net} kcal")
else:
    print(f"Total Burned (7d):    {total_burn} kcal (Avg {total_burn/7:.0f}/day)")
    print("No consumed calories logged (MyFitnessPal data missing or 0).")
