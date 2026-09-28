import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

act_id = 24526482716
new_name = "W15D1: Boxing & Heavy Bag Priming [21m]"
print(f"Renaming activity {act_id} to '{new_name}'...")
try:
    client.set_activity_name(act_id, new_name)
    print(f"[OK] Activity {act_id} renamed to '{new_name}' successfully!")
except Exception as e:
    print(f"[ERR] Failed to rename: {e}")
