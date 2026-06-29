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

today = date.today()
start_date = today - timedelta(days=6) # 7 days total including today

print("Date | Total Calories | Active Calories | BMR/Resting")
total_cal = 0
active_cal = 0

for i in range(7):
    current = start_date + timedelta(days=i)
    # Get daily stats
    stats = client.get_stats(current.isoformat())
    t_cal = stats.get("totalKilocalories", 0)
    a_cal = stats.get("activeKilocalories", 0)
    b_cal = stats.get("bmrKilocalories", 0)
    
    total_cal += t_cal
    active_cal += a_cal
    
    print(f"{current.isoformat()} | {t_cal} kcal | {a_cal} kcal | {b_cal} kcal")

print("-" * 50)
print(f"7-Day Total: {total_cal} kcal")
print(f"7-Day Average TDEE: {total_cal / 7:.0f} kcal")
print(f"Total Active Calories: {active_cal} kcal")
