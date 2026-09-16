"""
fetch_calories_aug8.py
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

today = date(2026, 8, 8).isoformat()

try:
    stats = client.get_user_summary(today)
    print("=== DAILY CALORIC SUMMARY (AUG 8) ===")
    print(f"Total Kilocalories: {stats.get('totalKilocalories')}")
    print(f"Active Kilocalories: {stats.get('activeKilocalories')}")
    print(f"BMR Kilocalories: {stats.get('bmrKilocalories')}")
except Exception as e:
    print(f"Summary failed: {e}")
