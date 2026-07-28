import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date, timedelta

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date.today().isoformat()

# Try user summary for body battery and recovery
try:
    bb = client.get_body_battery(today, today)
    print("Body Battery data:", json.dumps(bb, indent=2)[:500])
except Exception as e:
    print(f"Body battery error: {e}")

# Training readiness
try:
    tr = client.get_training_readiness(today)
    print("Training Readiness:", json.dumps(tr, indent=2)[:500])
except Exception as e:
    print(f"Training readiness error: {e}")

# All stats — dump all keys
try:
    stats = client.get_stats_and_body(today)
    print("\nStats keys:", list(stats.keys())[:30])
    for k in ["bodyBattery", "recoveryTime", "trainingLoad", "trainingStatus", "acuteLoad", "epoc"]:
        if k in stats:
            print(f"  {k}: {stats[k]}")
except Exception as e:
    print(f"Stats error: {e}")
