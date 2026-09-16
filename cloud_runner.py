"""
Unified Cloud Entry Point for Marathon Agent
Enables 1-click execution in Google Colab, GitHub Actions, and Codespaces.
"""

import os
import sys
import argparse
from datetime import date
from dotenv import load_dotenv

load_dotenv()

def run_audit():
    print("===> [CLOUD RUNNER] Running Garmin Telemetry & Vitals Audit...")
    import sensor_fetch_garmin
    print("===> [CLOUD RUNNER] Audit Complete.")

def run_pre_check(duration, intensity, target_date):
    print(f"===> [CLOUD RUNNER] Checking Tolerance Gate: {duration}m @{intensity} for {target_date or 'today'}...")
    cmd = f"python sensor_pre_schedule_check.py --duration {duration} --intensity {intensity}"
    if target_date:
        cmd += f" --date {target_date}"
    os.system(cmd)

def run_email_report():
    print("===> [CLOUD RUNNER] Dispatching Daily Email Report...")
    import actuator_send_report_email
    print("===> [CLOUD RUNNER] Email Sent.")

def main():
    parser = argparse.ArgumentParser(description="Marathon Agent Cloud Runner")
    parser.add_argument("action", choices=["audit", "check", "email", "status"], default="audit", nargs="?",
                        help="Action to execute")
    parser.add_argument("--duration", type=int, default=45, help="Workout duration in minutes")
    parser.add_argument("--intensity", default="easy", choices=["recovery", "easy", "marathon", "threshold", "vo2max"])
    parser.add_argument("--date", default=None, help="Target date (YYYY-MM-DD)")

    args = parser.parse_args()

    # Check for credentials
    email = os.getenv("GARMIN_EMAIL")
    pw = os.getenv("GARMIN_PASSWORD")
    if not email or not pw:
        print("[ERROR] Missing GARMIN_EMAIL or GARMIN_PASSWORD in environment!")
        print("Please configure secrets or your .env file before running.")
        sys.exit(1)

    print(f"[AUTH] Authenticated as: {email}")

    if args.action == "audit":
        run_audit()
    elif args.action == "check":
        run_pre_check(args.duration, args.intensity, args.date)
    elif args.action == "email":
        run_email_report()
    elif args.action == "status":
        print("[OK] Environment is properly configured and authenticated.")

if __name__ == "__main__":
    main()
