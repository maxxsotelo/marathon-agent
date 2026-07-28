import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

details = client.get_activity_splits("23486273442")
laps = details.get("lapDTOs", [])

total_gain = 0
total_loss = 0

print("Lap-by-lap elevation breakdown:")
print(f"{'Lap':<5} {'Type':<12} {'Dist(m)':<9} {'Pace':<9} {'AvgHR':<7} {'EleGain':<9} {'EleLoss':<9} {'MaxElev':<9} {'MinElev':<9}")
print("-" * 85)
for i, lap in enumerate(laps):
    dist = lap.get("distance", 0)
    dur = lap.get("duration", 0)
    avg_hr = lap.get("averageHR", 0)
    intensity = lap.get("intensityType", "N/A")
    gain = lap.get("elevationGain", 0) or 0
    loss = lap.get("elevationLoss", 0) or 0
    max_elev = lap.get("maxElevation", 0)
    min_elev = lap.get("minElevation", 0)
    total_gain += gain
    total_loss += loss
    if dur > 0 and dist > 0:
        pace_secs = dur / (dist / 1000)
        pace_min = int(pace_secs // 60)
        pace_sec = int(pace_secs % 60)
        pace_str = f"{pace_min}:{pace_sec:02d}"
    else:
        pace_str = "N/A"
    print(f"{i+1:<5} {intensity:<12} {dist:<9.0f} {pace_str:<9} {avg_hr:<7.0f} +{gain:<8.0f} -{loss:<8.0f} {max_elev:<9.1f} {min_elev:<9.1f}")

print()
print(f"TOTAL ELEVATION GAIN: +{total_gain:.0f}m")
print(f"TOTAL ELEVATION LOSS: -{total_loss:.0f}m")
print(f"Net: {total_gain - total_loss:+.0f}m")
