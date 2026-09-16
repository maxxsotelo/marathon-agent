"""
fetch_training_status.py
"""
import os, sys, json
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date(2026, 8, 7).isoformat()

try:
    status = client.get_training_status(today)
    print("=== TRAINING STATUS ===")
    print(f"Status: {status.get('trainingStatus')}")
    print(f"Load: {status.get('loadStatus')}")
    print(f"Recovery Hours: {status.get('recoveryTime')}")
except Exception as e:
    print(f"Status failed: {e}")

try:
    stats = client.get_user_summary(today)
    print("\n=== USER SUMMARY ===")
    print(f"Sleep Score: {stats.get('sleepScore')}")
    print(f"Sleep Hours: {stats.get('totalSleepSeconds', 0)/3600:.2f}")
    print(f"Body Battery (High): {stats.get('highestBodyBattery')}")
except Exception as e:
    print(f"Summary failed: {e}")
