import os
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv(r'c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env')
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

details = client.get_activity(23440767740)

# Print all top-level keys to understand structure
print("Top-level keys:", list(details.keys()))

# Try different lap structures
for key in ["splits", "laps", "activityDetailMetrics", "summaryDTO"]:
    val = details.get(key)
    if val is not None:
        print(f"\n--- {key} ---")
        if isinstance(val, dict):
            print("Sub-keys:", list(val.keys()))
        elif isinstance(val, list):
            print(f"List of {len(val)} items")
            if val:
                print("First item keys:", list(val[0].keys()) if isinstance(val[0], dict) else val[0])
