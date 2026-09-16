"""
fetch_pr_aug5_v2.py
Deep probe of metadataDTO and splitSummaries to find PR flags.
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
    
    print("=== METADATA DTO ===")
    meta = details.get('metadataDTO', {})
    print(json.dumps(meta, indent=2))
    
    print("\n=== SPLIT SUMMARIES ===")
    splits = details.get('splitSummaries', [])
    print(json.dumps(splits, indent=2))

    print("\n=== SUMMARY DTO (full) ===")
    summary = details.get('summaryDTO', {})
    print(json.dumps(summary, indent=2))

except Exception as e:
    print(f"Error: {e}")
