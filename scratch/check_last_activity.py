import os
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()
client = Garmin(os.getenv('GARMIN_EMAIL'), os.getenv('GARMIN_PASSWORD'))
client.login(os.path.expanduser('~/.garminconnect'))

activities = client.get_activities(0, 1)
if activities:
    act = activities[0]
    print(f"Activity Name: {act.get('activityName')}")
    print(f"Sport: {act.get('sportTypeId')}")
    print(f"Duration: {act.get('duration', 0)/60:.1f} mins")
    print(f"Distance: {act.get('distance', 0)/1000:.2f} km")
    print(f"Avg HR: {act.get('averageHR')}")
    print(f"Max HR: {act.get('maxHR')}")
    print(f"Training Effect: {act.get('aerobicTrainingEffect')}")
else:
    print('No activities found.')
