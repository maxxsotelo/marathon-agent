import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

acts = client.get_activities_by_date("2026-07-08", "2026-07-08")
strength_act = next((a for a in acts if "strength" in a.get("activityType", {}).get("typeKey", "")), None)

if not strength_act:
    print("No strength activity found for today.")
    sys.exit(0)

act_id = strength_act["activityId"]
print(f"Fetching details for activity {act_id}...")

details = client.get_activity_exercise_sets(str(act_id))
sets = details.get("exerciseSets", [])

print("\n--- Gym Session Log ---")
for s in sets:
    setType = s.get("setType", "")
    if setType == "REST":
        continue
    cat = s.get("category", "")
    sub_cat = s.get("subCategory", "")
    reps = s.get("repCount", 0)
    weight = s.get("weight", 0) / 1000 if s.get("weight") else 0
    print(f"Exercise: {cat} - {sub_cat} | Reps: {reps} | Weight: {weight}kg")
