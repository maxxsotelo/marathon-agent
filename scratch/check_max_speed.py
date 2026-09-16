import os, sys, json
from datetime import date
from dotenv import load_dotenv
load_dotenv(r'c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env')
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser('~/.garminconnect')
client = Garmin(email=os.getenv('GARMIN_EMAIL'), password=os.getenv('GARMIN_PASSWORD'))
client.login(TOKEN_STORE)

# 1. Check Personal Records
try:
    prs = client.get_personal_record()
    print('=== PERSONAL RECORDS ===')
    for pr in prs:
        type_key = pr.get('typeKey')
        formatted = pr.get('formattedValue')
        act_id = pr.get('activityId')
        print(f'PR: {type_key} -> {formatted} (ActivityId: {act_id})')
except Exception as e:
    print('PR err:', e)

# 2. Search activities for top maxSpeed
print('\n=== SCANNING ACTIVITIES FOR TOP MAX SPEED ===')
acts = client.get_activities(0, 200) # Get last 200 activities
speed_records = []
for a in acts:
    aid = a.get('activityId')
    name = a.get('activityName')
    date_str = a.get('startTimeLocal', '')[:10]
    atype = a.get('activityType', {}).get('typeKey', '')
    max_spd = a.get('maxSpeed', 0) or 0 # in m/s
    if 'running' in atype or 'treadmill' in atype or 'track' in atype:
        kph = max_spd * 3.6
        pace_s = 1000.0 / max_spd if max_spd > 0 else 0
        speed_records.append({
            'activityId': aid,
            'date': date_str,
            'name': name,
            'type': atype,
            'max_kph': kph,
            'max_pace': pace_s,
            'distance_km': (a.get('distance', 0) or 0) / 1000
        })

speed_records.sort(key=lambda x: x['max_kph'], reverse=True)

print(f'\nTop 15 Fastest Maximum Speeds in Garmin History (out of {len(speed_records)} runs):')
for i, r in enumerate(speed_records[:15], 1):
    pace_min = int(r['max_pace'] // 60)
    pace_sec = int(r['max_pace'] % 60)
    kph = r['max_kph']
    d = r['date']
    n = r['name']
    aid = r['activityId']
    print(f'{i:2d}. {kph:5.2f} km/h ({pace_min}:{pace_sec:02d}/km) | Date: {d} | Name: {n} | ActId: {aid}')
