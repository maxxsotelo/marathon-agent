"""
fetch_readiness_status.py
Fetches Garmin Training Readiness and HRV Status for the current date.
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

# Fetch HRV Status
try:
    hrv = client.get_hrv_data(today)
    print("=== HRV STATUS ===")
    print(f"Status: {hrv.get('hrvStatus')}")
    print(f"7-day Avg: {hrv.get('last7DaysAvg')} ms")
    print(f"Last Night: {hrv.get('lastNightAvg')} ms")
except Exception as e:
    print(f"Failed to fetch HRV status: {e}")

print()

# Fetch Training Readiness
try:
    readiness = client.get_training_readiness(today)
    print("=== TRAINING READINESS ===")
    print(f"Readiness Score: {readiness.get('latestReadinessScore')}")
    print(f"Readiness Category: {readiness.get('latestReadinessCategory')}")
    
    # Sub-components if available
    components = readiness.get('components', [])
    for comp in components:
        print(f" - {comp.get('componentType')}: {comp.get('category')} ({comp.get('value')})")
except Exception as e:
    print(f"Failed to fetch Training Readiness: {e}")
