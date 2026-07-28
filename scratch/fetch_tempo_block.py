import os
import json
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv(r'c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env')
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

details = client.get_activity(23440767740)
splits = details.get("splitSummaries", [])

print("=== TEMPO BLOCK DETAILS ===")
for sp in splits:
    if sp.get("splitType") == "INTERVAL_ACTIVE":
        dist = round((sp.get("distance") or 0) / 1000, 2)
        dur = round((sp.get("duration") or 0) / 60, 1)
        spd = sp.get("averageSpeed", None)
        pace_str = "N/A"
        if spd and spd > 0:
            p = 1000 / spd / 60
            pace_str = f"{int(p)}:{int((p - int(p))*60):02d} /km"
            
        print(f"Distance: {dist} km")
        print(f"Duration: {dur} min")
        print(f"Avg Pace: {pace_str}")
        print(f"Avg HR:   {sp.get('averageHR')} bpm")
        print(f"Max HR:   {sp.get('maxHR')} bpm")
        print(f"Avg Cad:  {sp.get('averageRunCadence')} spm")
        print(f"Max Cad:  {sp.get('maxRunCadence')} spm")
        print(f"Elev Gain:{sp.get('elevationGain')} m")
        
        # Dump full split dict to see if there are other useful metrics
        # print("\nFull split data:", json.dumps(sp, indent=2))
