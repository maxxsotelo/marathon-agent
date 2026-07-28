import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

details = client.get_activity_splits("23497291370")
laps = details.get("lapDTOs", [])

print("Rainy Run with Tops — Jul 6, 2026 | Lap-by-lap")
print(f"{'Lap':<5} {'Type':<12} {'Dist(m)':<9} {'Pace':<9} {'AvgHR':<7} {'MaxHR':<7} {'Cad':<7} {'GCT':<8} {'Stride':<9} {'EleG':<6} {'EleL':<6}")
print("-" * 90)

total_gain = 0
total_loss = 0

for i, lap in enumerate(laps):
    dist = lap.get("distance", 0) or 0
    dur = lap.get("duration", 0) or 0
    avg_hr = lap.get("averageHR", 0) or 0
    max_hr = lap.get("maxHR", 0) or 0
    cad = lap.get("averageRunCadence", 0) or 0
    gct = lap.get("groundContactTime", 0) or 0
    stride = lap.get("strideLength", 0) or 0
    intensity = lap.get("intensityType", "N/A")
    gain = lap.get("elevationGain", 0) or 0
    loss = lap.get("elevationLoss", 0) or 0
    total_gain += gain
    total_loss += loss

    if dur > 0 and dist > 0:
        pace_secs = dur / (dist / 1000)
        pace_str = f"{int(pace_secs//60)}:{int(pace_secs%60):02d}"
    else:
        pace_str = "N/A"

    print(f"{i+1:<5} {intensity:<12} {dist:<9.0f} {pace_str:<9} {avg_hr:<7.0f} {max_hr:<7.0f} {cad:<7.1f} {gct:<8.1f} {stride:<9.1f} +{gain:<5.0f} -{loss:<5.0f}")

print()
print(f"Total Elevation Gain: +{total_gain:.0f}m | Loss: -{total_loss:.0f}m")
