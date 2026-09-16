"""
fetch_run_telemetry_v2.py
Uses get_activity_details to pull the richest telemetry for the Jul 30 track session.
"""
import os, sys, json
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

act_id = 23785707297  # Jul 30 track run

# Try get_activity_details which returns metrics samples
try:
    details = client.get_activity_details(act_id, maxchartsize=2000)
    # Print top level keys
    print("Top-level keys:", list(details.keys()))
    
    # geoPolylineDTO, activityDetailMetrics, metricDescriptors
    descriptors = details.get('metricDescriptors', [])
    print(f"\nAvailable metrics ({len(descriptors)}):")
    for d in descriptors:
        print(f"  [{d.get('metricsIndex')}] {d.get('key')} ({d.get('unit', {}).get('key', '')})")
    
    # Pull first and last few samples to see what data looks like
    samples = details.get('activityDetailMetrics', [])
    print(f"\nTotal samples: {len(samples)}")
    if samples:
        print("\nFirst 3 samples:")
        for s in samples[:3]:
            print(f"  {s.get('metrics')}")
        print("\nLast 3 samples:")
        for s in samples[-3:]:
            print(f"  {s.get('metrics')}")
except Exception as e:
    print(f"get_activity_details failed: {e}")

# Try fetching laps with full data
try:
    splits = client.get_activity_splits(act_id)
    print("\n=== FULL LAP TELEMETRY ===")
    for i, lap in enumerate(splits.get('lapDTOs', [])):
        dist = lap.get('distance', 0)
        dur = lap.get('duration', 0)
        avg_hr = lap.get('averageHR', 'N/A')
        max_hr = lap.get('maxHR', 'N/A')
        cadence = lap.get('averageRunCadence', 'N/A')
        stride = lap.get('avgStrideLength', 'N/A')
        gct = lap.get('avgGroundContactTime', 'N/A')
        vosc = lap.get('avgVerticalOscillation', 'N/A')
        power = lap.get('avgPower', 'N/A')
        
        if dist > 50:
            pace_sec = dur / (dist / 1000)
            pace_min = int(pace_sec // 60)
            pace_s = int(pace_sec % 60)
            pace_str = f"{pace_min}:{pace_s:02d}/km"
        else:
            pace_str = "N/A"
            
        print(f"  Lap {i+1} [{dist:.0f}m | {dur:.0f}s | {pace_str}]")
        print(f"    HR: {avg_hr}/{max_hr} bpm | Cadence: {cadence} spm | Stride: {stride}m")
        print(f"    GCT: {gct}ms | VOsc: {vosc}cm | Power: {power}W")
except Exception as e:
    print(f"Laps failed: {e}")
