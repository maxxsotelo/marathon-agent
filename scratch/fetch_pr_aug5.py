"""
fetch_pr_aug5.py
Check PRs from today's run activity directly.
"""
import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

ACT_ID = 23860862117

try:
    details = client.get_activity(ACT_ID)
    # Dump a selection of top-level keys to find where PRs live
    print("=== TOP-LEVEL KEYS IN ACTIVITY DETAIL ===")
    for k, v in details.items():
        if isinstance(v, (dict, list)):
            print(f"  {k}: {type(v).__name__} ({len(v)} items)")
        else:
            print(f"  {k}: {v}")
except Exception as e:
    print(f"Error: {e}")
