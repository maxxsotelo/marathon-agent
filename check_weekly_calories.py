import os
import sys
from datetime import date, timedelta
sys.path.insert(0, r'c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent')
from dotenv import load_dotenv
load_dotenv(r'c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env')
from garminconnect import Garmin

client = Garmin(email=os.getenv('GARMIN_EMAIL'), password=os.getenv('GARMIN_PASSWORD'))
client.login(os.path.expanduser('~/.garminconnect'))

today = date.today()
days = [today - timedelta(days=i) for i in range(6, -1, -1)]

print('Date       | Burned | Consumed | Net')
print('-' * 40)
total_burned = 0
total_consumed = 0

for d in days:
    try:
        s = client.get_user_summary(d.isoformat())
        b = s.get('totalKilocalories', 0)
        c = s.get('consumedKilocalories', 0) if s.get('consumedKilocalories') else 0
        net = c - b if c > 0 else 0
        print(f"{d.isoformat()} | {int(b):>6} | {int(c):>8} | {int(net):>5}")
        total_burned += b
        total_consumed += c
    except Exception as e:
        print(f"{d.isoformat()} | Error fetching: {e}")

print('-' * 40)
net_total = total_consumed - total_burned if total_consumed > 0 else 0
print(f"TOTAL      | {int(total_burned):>6} | {int(total_consumed):>8} | {int(net_total):>5}")
