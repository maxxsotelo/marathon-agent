import os

replacements = {
    # physiological_engine.py
    '(1, "Z1-Recovery",   0,   144)': '(1, "Z1-Easy_Aerobic",  0,   161)',
    '(2, "Z2-Aerobic",    145, 162)': '(2, "Z2-Extensive",     162, 174)',
    '(3, "Z3-Grey/MP",    163, 184)': '(3, "Z3-Tempo",         175, 181)',
    '(4, "Z4-Threshold",  185, 196)': '(4, "Z4-Threshold",     182, 191)',
    '(5, "Z5-Anaerobic",  197, 999)': '(5, "Z5-VO2_Max",       192, 999)',
    'ZONE2_CAP_BPM = 162': 'ZONE2_CAP_BPM = 174',
    '145 <= l.avg_hr <= ZONE2_CAP_BPM': '162 <= l.avg_hr <= ZONE2_CAP_BPM',
    'HR 145–162 bpm': 'HR 162-174 bpm',
    
    # send_report_email.py
    '<145 bpm': '<162 bpm',
    '145-162 bpm': '162-174 bpm',
    '163-184 bpm': '175-181 bpm',
    '185-196 bpm': '182-191 bpm',
    '197+ bpm': '192+ bpm',
    
    # antigravity_core.py
    'Z1 <145 | Z2 145-162 | Z3 163-184 | Z4 185-196 | Z5 197+': 'Z1 <162 | Z2 162-174 | Z3 175-181 | Z4 182-191 | Z5 192+',

    # knowledge_base markdown files
    '145–162 bpm': '162–174 bpm',
    '145-162 bpm': '162-174 bpm',
    '< 145 bpm': '< 162 bpm',
    '163 – 184 bpm': '175 – 181 bpm',
    '163–184 bpm': '175–181 bpm',
    '185 – 196 bpm': '182 – 191 bpm',
    '185–196 bpm': '182–191 bpm',
    '197+ bpm': '192+ bpm',
    '163–180 bpm': '175–181 bpm',
    '163–196 bpm': '175–191 bpm',
    
    # Bike zones cross training
    '145–150 bpm': '150–155 bpm',
}

files = [
    "antigravity_core.py",
    "physiological_engine.py",
    "send_report_email.py",
    "knowledge_base/knowledge_base.md",
    "knowledge_base/cross_training_cycling_swimming.md",
    "knowledge_base/maintenance_and_weight_loss.md",
    "knowledge_base/operating_manual.md",
    "knowledge_base/speed_and_endurance_development.md",
]

for f in files:
    path = os.path.join(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent", f)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated {f}")
