import os
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv(r'c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env')
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

# Fetch laps for the tempo run
details = client.get_activity(23440767740)
laps = details.get("splits", {}).get("lapDTOs", [])

print(f"=== Tempo Run Lap Breakdown ===")
print(f"Total laps: {len(laps)}")
for i, lap in enumerate(laps):
    lkm = round((lap.get("distance") or 0) / 1000, 2)
    lhr = lap.get("averageHR", "N/A")
    lmax = lap.get("maxHR", "N/A")
    lspd = lap.get("averageSpeed", None)
    lcad = lap.get("averageRunCadence", "N/A")
    if lspd and lspd > 0:
        lp = 1000 / lspd / 60
        lpace = f"{int(lp)}:{int((lp - int(lp)) * 60):02d}"
    else:
        lpace = "N/A"
    print(f"  Lap {i+1:2d}: {lkm:5.2f} km | {lpace} /km | Avg HR: {lhr} | Max HR: {lmax} | Cad: {lcad}")
