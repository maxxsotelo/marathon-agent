import os, sys, json
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

activity_ids = sys.argv[1:]
if not activity_ids:
    print("Provide activity IDs as arguments")
    sys.exit(1)

for act_id in activity_ids:
    print(f"\n=== ACTIVITY {act_id} ===")
    try:
        details = client.get_activity(act_id)
        name = details.get("activityName", "Unknown")
        print(f"Name: {name}")
        sets = client.get_activity_exercise_sets(act_id)
        
        if sets.get('exerciseSets'):
            print("Raw first set keys:", list(sets['exerciseSets'][0].keys()))
            print("Raw first set:", json.dumps(sets['exerciseSets'][0]))
            
        for s in sets.get('exerciseSets', []):
            reps = s.get('repetitionCount', 0)
            weight = s.get('weight', 0) / 1000 if s.get('weight') else 0
            
            ex_list = s.get('exercises', [])
            ex_name = ex_list[0].get('name') if ex_list else "Unknown"
            
            if s.get('setType') == "ACTIVE":
                print(f"  Set: {reps} reps | {weight} kg | {ex_name}")
            
    except Exception as e:
        print(f"Error fetching {act_id}: {e}")
