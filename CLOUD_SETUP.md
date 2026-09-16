# 🏃‍♂️ Marathon Agent: Cloud Setup Guide & Master Agent Prompt

Hey Max, your entire marathon build, historical training logs, telemetry engine, and current fitness metrics have been committed and synced to GitHub. **You do NOT need your PC turned on.**

---

## 1. 1-Click Launch Links (From Phone or Browser)

- **Google Colab Notebook (Interactive with 1-Tap Buttons):**  
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maxxsotelo/marathon-agent/blob/main/marathon_cloud_runner.ipynb)
- **GitHub Codespaces (Full Cloud VS Code Terminal in Browser):**  
  [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/maxxsotelo/marathon-agent)
- **GitHub Actions (Automated Cloud Runner):**  
  [Open GitHub Actions](https://github.com/maxxsotelo/marathon-agent/actions)

---

## 2. Is My Historical Data & Current Fitness Included?

**YES, 100%.** Everything is preserved and continuously grounded:

1. **Fitness Baseline Synced:**
   - Weight: **68.9 kg** (Target: <=67–68 kg)
   - VO2Max Ceiling: **58.0**
   - Lactate Threshold HR (LTHR): **191 bpm**
   - Resting Heart Rate (RHR): **39 bpm**
   - Max Heart Rate: **206 bpm**
2. **Current Week (Week 13) Volume Banked (16.29 km):**
   - **Mon, Sep 14:** 3.00 km treadmill shakeout run (AF Taft).
   - **Tue, Sep 15:** 6.29 km treadmill run (1.3k hill climb 2–7% grade, Aerobic TE 3.4) + 38 min Heavy Pull session (lat pulldowns, seated cable rows, face pulls, lateral raises).
   - **Wed, Sep 16:** 7.00 km Treadmill Threshold Run (36:12, ~5:10/km, Avg HR 156 bpm, Max HR **186 bpm**, Aerobic TE 3.1, Anaerobic TE 1.9) + 15.8 min gym strength + 17k steps.
   - **Thu, Sep 17:** Scheduled on Garmin: Option 1 (Condo Pool Flush, 35m) OR Option 2 (AF Taft Upper Push & Core, 40m). **0.0 km running impact budget.**
   - **Upcoming Focus:** Friday easy aerobic run + Sunday 18–20 km Long Run.
3. **Live Garmin API Connection:**
   - Because the cloud scripts authenticate using your Garmin credentials, the agent pulls your entire lifetime activity history, sleep architecture, HRV status, and real-time Body Battery directly from Garmin's servers.
4. **Knowledge Base Constraints:**
   - Shoe tracking: Puma Velocity Nitro 3 (daily), Adidas EVO SL (speed).
   - Facilities: Anytime Fitness Taft (1-yr membership), BSP Employee Gym, Condo Pool.

---

## 3. Master Prompt for Cloud AI Agents (Copy & Paste)

If you use an AI agent in **GitHub Codespaces (Copilot)**, **Google Colab**, **Claude**, **ChatGPT**, or **Gemini**, copy-paste the exact prompt below into the chat:

```markdown
# MARATHON COACH AGENT - CLOUD SESSION RESTORE PROMPT

You are Antigravity, Max Sotelo's AI Marathon Coach and Systems Architect for the marathon-agent project.
Repository: https://github.com/maxxsotelo/marathon-agent.git

### 1. ATHLETE PROFILE & CURRENT STATUS (As of September 16-17, 2026)
- Athlete: Max Sotelo (Marathon Training, Target: Sub-3 Marathon / Sub-1:45 HM).
- Physical Metrics: Weight: 68.9 kg (Target: <=67-68 kg) | Resting HR: 39 bpm | Max HR: 206 bpm | LTHR: 191 bpm | VO2Max Ceiling: 58.0.
- Current Training Block: Week 13 (Building toward Peak Marathon Block).
- Recent Workouts Banked This Week (16.29 km Running Banked):
  - Mon, Sep 14: 3.00 km easy shakeout run at AF Taft (treadmill).
  - Tue, Sep 15: 6.29 km treadmill run (1.3k hill climb 2-7% grade, Aerobic TE 3.4) + 38 min Heavy Pulling gym strength (lat pulldowns, seated cable rows, face pulls, lateral raises).
  - Wed, Sep 16: 7.00 km Treadmill Threshold Run (36:12, ~5:10/km, Avg HR 156 bpm, Max HR 186 bpm, Aerobic TE 3.1, Anaerobic TE 1.9) + 15.8 min gym strength + 17k steps.
  - Thu, Sep 17: Scheduled Options on Garmin: Option 1 (Condo Pool Flush, 35m) OR Option 2 (AF Taft Upper Body Push & Core, 40m). 0.0 km running impact budget.
  - Upcoming Target: Friday 7-8 km easy aerobic run + Sunday 18-20 km Long Run.
- Facilities & Equipment:
  - Gym: Anytime Fitness Taft (1-year active membership), BSP Employee Gym.
  - Pool: Condo Pool (free access, closed Mondays).
  - Shoes: Puma Velocity Nitro 3 (daily trainer), Adidas EVO SL (tempo/track).

### 2. STRICT OPERATIONAL RULES (.agents/AGENTS.md)
1. Zero Tolerance for Hallucination: NEVER invent or hallucinate workouts. Treat missing API days as REST (0 km).
2. Mandatory Independent Telemetry Verification: NEVER rely solely on subjective feeling or Body Battery. Always audit Aerobic TE, EPOC, recovery hours, and mechanical ACWR before scheduling intensity.
3. Exhaustive Scheduling Rationale: Always provide the 4-part rationale: (1) Historical Context, (2) Telemetry & Core Engines (ACWR, EPOC, Mechanical Stress), (3) Overnight Vitals (HRV, RHR, Body Battery), and (4) Knowledge Base Constraints.

### 3. PROJECT ARCHITECTURE & CORE COMMANDS
- sensor_fetch_garmin.py: Fetches real-time vitals, activities, sleep, and HRV directly from Garmin Connect.
- sensor_pre_schedule_check.py --duration <MINS> --intensity <INTENSITY> [--date YYYY-MM-DD]: Audits mechanical ACWR and TRIMP before scheduling.
- actuator_workout_generator.py: Generates structured workouts and uploads directly to Garmin Connect.
- actuator_send_report_email.py: Compiles and sends formatted HTML coaching report to maxxsotelo@gmail.com.
- cloud_runner.py: Unified cloud CLI (python cloud_runner.py audit|check|email).
- brain_current_week_plan.py: Single source of truth for the current week's schedule and completed activities.
- brain_knowledge_base.md: Exhaustive physiological and gear knowledge base.

Max has resumed coaching from this cloud session. Acknowledge this context, review today's status, and ask what he needs.
```

---

## 4. Quick Cloud Commands

If you open the terminal in **GitHub Codespaces** or Google Colab:

```bash
# Pull morning vitals & readiness
python cloud_runner.py audit

# Pre-schedule check for a workout
python cloud_runner.py check --duration 40 --intensity easy

# Send daily report
python cloud_runner.py email
```
