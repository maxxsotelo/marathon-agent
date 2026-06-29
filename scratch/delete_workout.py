import os
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

try:
    client.delete_workout("1610505373")
    print("Successfully deleted workout 1610505373")
except Exception as e:
    print(f"Failed to delete: {e}")
