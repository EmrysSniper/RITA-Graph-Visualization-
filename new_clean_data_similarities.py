import json
import re
import csv
from collections import defaultdict
import pandas as pd
from pathlib import Path

# -------- CONFIG --------
DATA_FILE = "C:\\Users\\olaye\\Documents\\UARC\\semantic_enriched_output.json"
OUTPUT_JSON = "C:\\Users\\olaye\\Documents\\UARC\\aircraft_by_similarity_theme.json"

# Define similarity themes and regex patterns
THEMES = {
    "Stall / Stall_spin"       : r"stall|critical angle|spin|loss of lift|loss of airspeed",
    "Fuel starvation"          : r"fuel starvation|fuel selector|water in fuel|tank ran dry",
    "Landing_gear failure"     : r"landing gear (collapsed|fractured|separated)|ground loop",
    "Tail_strike"              : r"tailstrike|pitch .*degrees|toga thrust",
    "Wire / tree strike"       : r"wire strike|power line|struck (trees|power lines)",
    "Spatial disorientation"   : r"spatial disorientation|entered.*cloud|steep descent",
    "Engine_component failure" : r"oil starvation|exhaust valve|idle valve|drive gear",
}

# Aircraft manufacturer keywords for filtering
MANUFACTURERS = {
    "airbus", "boeing", "cessna", "piper", "beech", "beechcraft", "mooney", "cirrus",
    "lancair", "ryan", "douglas", "mcdonnell", "north", "extra", "air", "airtractor",
    "aeronca", "grumman", "yak", "zenith", "glasair", "vans", "poberezny", "moth",
    "wheeler", "navion", "kitfox", "titan", "weatherly"
}

def is_probable_aircraft(name: str) -> bool:
    """Return True if string looks like an aircraft model (basic heuristic)."""
    n = name.strip()
    if not n:
        return False
    if re.fullmatch(r"\d{4}", n) or re.fullmatch(r"N\d+[A-Z]*", n):
        return False
    first_word = n.split()[0].lower()
    if re.search(r"\d", n) or first_word in MANUFACTURERS:
        return True
    return False

# -------- LOAD DATA --------
with open(DATA_FILE, encoding="utf-8") as f:
    records = json.load(f)

# -------- GROUP BY THEME --------
theme_aircraft = defaultdict(set)
for rec in records:
    blob = " ".join(rec["damage_notes"] + rec["cause_notes"] + rec["keywords"]).lower()
    aircraft_clean = set()
    for entry in rec.get("aircraft", []):
        for token in re.split(r"[;/,]", entry):
            token = token.strip()
            if is_probable_aircraft(token):
                aircraft_clean.add(token)

    for theme, pattern in THEMES.items():
        if re.search(pattern, blob):
            theme_aircraft[theme].update(aircraft_clean)

# -------- EXPORT --------
# Save as JSON
theme_aircraft_output = {k: sorted(v) for k, v in theme_aircraft.items()}
with open(OUTPUT_JSON, "w", encoding="utf-8") as f_json:
    json.dump(theme_aircraft_output, f_json, indent=2)


print("[✔] Export complete:")
print(f"    • JSON:  {OUTPUT_JSON}")

