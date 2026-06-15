import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

# Get today's activities to find the strength session ID
activities = client.get_activities_by_date("2026-05-27", "2026-05-27")
strength_id = None
for act in activities:
    if act.get("activityType", {}).get("typeKey") == "strength_training":
        strength_id = act.get("activityId")
        print(f"Found strength session: {act.get('activityName')} | ID: {strength_id}")
        print(f"  Duration: {act.get('duration', 0)/60:.1f} min")
        print(f"  Avg HR: {act.get('averageHR')} bpm | Max HR: {act.get('maxHR')} bpm")
        print(f"  Calories: {act.get('calories')} kcal")
        break

if not strength_id:
    print("No strength session found today.")
    sys.exit(1)

print("\n=== EXERCISE SETS ===")
try:
    sets = client.get_activity_exercise_sets(strength_id)
    # Dump the raw structure to understand what we're working with
    print(json.dumps(sets, indent=2))
except Exception as e:
    print(f"Error: {e}")
