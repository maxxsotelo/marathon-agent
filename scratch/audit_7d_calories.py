import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(
    email=os.getenv("GARMIN_EMAIL"),
    password=os.getenv("GARMIN_PASSWORD"),
    prompt_mfa=lambda: input("MFA: "),
)
client.login(TOKEN_STORE)

today = date.today()
days = [today - timedelta(days=i) for i in range(7, 0, -1)]

print(f"=== 7-DAY CALORIC SITUATION AUDIT ({days[0]} to {days[-1]}) ===")
print("Date       | Day | Burned (TDEE) | Consumed (MFP) | Net Balance | Context")
print("-" * 75)

total_burned = 0
total_consumed = 0

day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

for d in days:
    try:
        s = client.get_user_summary(d.isoformat())
        b = s.get('totalKilocalories', 0)
        c = s.get('consumedKilocalories', 0) if s.get('consumedKilocalories') else 0
        net = c - b if (c > 0 and b > 0) else 0
        bmr = s.get('bmrKilocalories', 0)
        active = s.get('activeKilocalories', 0)
        d_name = d.strftime("%a")
        
        # Determine context
        ctx = ""
        if net < -300: ctx = "Solid Deficit"
        elif net < 0: ctx = "Mild Deficit"
        elif net < 200: ctx = "Near Maintenance"
        elif net < 500: ctx = "Mild Surplus"
        else: ctx = "Refeed / Surplus"

        print(f"{d.isoformat()} | {d_name} | {int(b):>8} kcal  | {int(c):>9} kcal   | {int(net):>+7} kcal | {ctx}")
        total_burned += b
        total_consumed += c
    except Exception as e:
        print(f"{d.isoformat()} | Error fetching: {e}")

print("-" * 75)
net_total = total_consumed - total_burned
avg_burned = total_burned / len(days)
avg_consumed = total_consumed / len(days)
avg_net = net_total / len(days)

print(f"7-DAY TOTALS  | {int(total_burned):>8} kcal  | {int(total_consumed):>9} kcal   | {int(net_total):>+7} kcal")
print(f"DAILY AVERAGE | {int(avg_burned):>8} kcal  | {int(avg_consumed):>9} kcal   | {int(avg_net):>+7} kcal/day")

# Also check today's current live burn/consumed so far
print("\n--- TODAY'S LIVE STATUS (Aug 19 so far) ---")
s_today = client.get_user_summary(today.isoformat())
b_today = s_today.get('totalKilocalories', 0)
c_today = s_today.get('consumedKilocalories', 0) if s_today.get('consumedKilocalories') else 0
print(f"  Burned so far (TDEE):   {int(b_today)} kcal (Active: {s_today.get('activeKilocalories')} kcal)")
print(f"  Consumed so far (MFP): {int(c_today)} kcal")
