# LSD Deep Dive Analysis — July 4, 2026 | EVO SL First LSD
# Activity ID: 23475268160

# Key metrics from raw Garmin data:
# Overall RUN block (RWD_RUN, 14,964m): avgHR 161, avg cadence 175, GCT 254ms, stride 103.85cm, VO 8.53cm, VR 8.24%
# WARMUP block (INTERVAL_WARMUP, 1,630m): avgHR 139, cadence 165.8, GCT 270.8ms, stride 97.3cm, VO 8.71cm, VR 8.97%
# ACTIVE block (INTERVAL_ACTIVE, 12,866m): avgHR 163, cadence 175.1, GCT 252.4ms, stride 104.16cm, VO 8.49cm, VR 8.17%
# KICK (INTERVAL_COOLDOWN used as kick, 514.82m): avgHR 183, cadence 178.7, GCT 234.5ms, stride 121.97cm, VO 8.97cm, VR 7.35%

# Temperature: avg 32.6°C, max 34°C → extreme heat load
# Power: avg 318W, normalized 324W
# Total steps: 14,400
# Water estimated lost: 1,372 ml
# Body Battery change: -14
# RPE logged: 40/100 (very comfortable)
# Feel logged: 50/100

print("=== ANALYSIS COMPLETE ===")
print("All metrics captured from Garmin splitSummaries")
