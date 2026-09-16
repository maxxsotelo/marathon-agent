"""
fetch_current_caloric_balance.py
"""
import os, sys, json
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

print(f"=== CALORIC BALANCE ({start_date} to {end_date}) ===")

total_burn = 0
total_consumed = 0
days_tracked = 0

for i in range(7):
    d = start_date + timedelta(days=i)
    try:
        # User summary contains totalKilocalories (burn)
        stats = client.get_user_summary(d.isoformat())
        burn = stats.get('totalKilocalories', 0)
        
        # Garmin nutrition API (synced from MFP) usually stores consumed in a different endpoint
        # or inside stats if MFP is linked. The old script might have used get_user_summary or get_nutrition_data.
        # Let's try to find the consumed calories. If it's in stats, great. 
        # If not, some garminconnect clients use get_consumed_kilocalories or similar.
        consumed = stats.get('consumedKilocalories', 0)
        
        if consumed == 0:
            # Fallback if it's stored differently
            consumed = stats.get('totalCaloriesConsumed', 0)
            
        # Or maybe it's in a separate nutrition endpoint: client.get_nutrition_data(d.isoformat())
        # The python-garminconnect package doesn't always have a direct nutrition wrapper, 
        # but let's assume it's in stats or we can just print what we find.
        # I'll just check if there's any nutrition-related keys.
        
        net = consumed - burn if consumed > 0 else 0
        net_str = f"+{net}" if net > 0 else f"{net}"
        
        if consumed > 0:
            print(f"{d.strftime('%a, %b %d')}: Burned {burn:.0f} kcal | Consumed {consumed:.0f} kcal | Net: {net_str}")
            total_burn += burn
            total_consumed += consumed
            days_tracked += 1
        else:
            print(f"{d.strftime('%a, %b %d')}: Burned {burn:.0f} kcal | Consumed data missing")
            
    except Exception as e:
        print(f"[{d.isoformat()}] Failed: {e}")

if days_tracked > 0:
    print("-" * 50)
    print(f"Total Burned ({days_tracked}d):    {total_burn:.0f} kcal")
    print(f"Total Consumed ({days_tracked}d):  {total_consumed:.0f} kcal")
    print(f"NET BALANCE:          {total_consumed - total_burn:.0f} kcal")
