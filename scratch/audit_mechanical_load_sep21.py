import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
from garminconnect import Garmin
from datetime import date
from core_tolerance_engine import calculate_mechanical_load

load_dotenv(r'c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env')
TOKEN_STORE = os.path.expanduser('~/.garminconnect')
client = Garmin(os.getenv('GARMIN_EMAIL'), os.getenv('GARMIN_PASSWORD'))
client.login(TOKEN_STORE)

target = date(2026, 9, 21)
res = calculate_mechanical_load(client, target_date=target)
print("=== MECHANICAL LOAD & ACWR AUDIT (SEP 21, 2026) ===")
for k, v in res.items():
    print(f"  {k}: {v}")

