# Marathon Agent Project Rules

These rules apply strictly to any AI agent working within the `marathon-agent` workspace. You must adhere to them at all times.

## 1. Zero Tolerance for Hallucination
- **NEVER** hallucinate or invent workout activities, shakeout runs, or training sessions to fill gaps in the calendar. 
- If a day does not have an activity explicitly logged in the Garmin API, you must treat it as a REST day or 0 km day. Do not infer activities based on what a traditional marathon plan "should" look like.

## 2. Mandatory Independent Telemetry Verification
- **NEVER** rely solely on the user's subjective sentiment (e.g., "I feel fresh today") or top-level scores (like "Training Readiness" or "Body Battery") to schedule a high-intensity workout (Zone 3, Zone 4, Threshold, VO2Max, or Long Runs).
- **ALWAYS** run an independent, deep telemetry audit of the last 7 days of training data before confirming or scheduling a hard workout. 
- You must explicitly pull and evaluate:
  - **Aerobic Training Effect (TE)** of recent sessions.
  - **EPOC / Load** of recent sessions.
  - **Recovery Hours** dictated by Garmin.
  - **Heat Index / Environmental Stress** if applicable.
- If the physiological strain from recent sessions (e.g., a TE 4.0 run 48 hours ago) contraindicates high-intensity work, you must VETO the request, even if the user claims to feel fully recovered. Rely strictly on cold hard numbers.
