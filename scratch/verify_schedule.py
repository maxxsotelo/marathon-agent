import os
from datetime import date
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(
    email=os.getenv("GARMIN_EMAIL"),
    password=os.getenv("GARMIN_PASSWORD"),
    prompt_mfa=lambda: input("MFA: "),
)
client.login(TOKEN_STORE)

today = date.today()
today_str = today.strftime("%Y-%m-%d")

print(f"Checking scheduled workouts for {today_str} on Garmin Connect...")

# Let's check calendar or schedule
workout_id = 1669857555
try:
    res = client.schedule_workout(workout_id, today_str)
    print(f"Schedule response for workout {workout_id}: {res}")
except Exception as e:
    print(f"Error: {e}")
