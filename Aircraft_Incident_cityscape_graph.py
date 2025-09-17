import plotly.graph_objects as go
import os
from collections import defaultdict

# File paths (update if needed)
flight_info_path =  "C:\\Users\\olaye\\Documents\\UARC\\Aircraft_names.txt"
injury_path = "C:\\Users\\olaye\\Documents\\UARC\\Injuries.txt"
damage_path = "C:\\Users\\olaye\\Documents\\UARC\\Aircraft Damage.txt"

# Load Aircraft and PDF associations
def load_flight_info(file_path):
    aircraft_to_pdfs = {}
    current_aircraft = None
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if not line.endswith('.pdf'):
                current_aircraft = line.rstrip(':')
                aircraft_to_pdfs[current_aircraft] = []
            else:
                aircraft_to_pdfs[current_aircraft].append(line)
    return aircraft_to_pdfs

# Parse category-style txt files (Injuries / Damage)
def parse_category_file(filepath):
    category_map = {}
    current_category = None
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if not line.endswith('.pdf'):
                current_category = line.rstrip(':')
            else:
                category_map[line] = current_category
    return category_map

# Injury and Damage Scoring
def map_injury_level(injury_set):
    if not injury_set or 'Unknown' in injury_set:
        return 0
    if any('Fatal' in i for i in injury_set):
        return 4
    if any('Serious' in i for i in injury_set):
        return 3
    if any('Minor' in i for i in injury_set):
        return 2
    if any('None' in i for i in injury_set):
        return 1
    return 0

def map_damage_level(damage_set):
    if not damage_set or 'Unknown' in damage_set:
        return 1.0
    if any("Destroyed" in d for d in damage_set):
        return 3.0
    if any("Substantial" in d for d in damage_set):
        return 2.0
    if any("Minor" in d for d in damage_set):
        return 1.5
    return 1.0

# Build 3D cube (bar)
def create_bar(x, y, z, dx, dy, dz, color, hovertext):
    x0, x1 = x, x + dx
    y0, y1 = y, y + dy
    z0, z1 = z, z + dz
    vertices = [
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ]
    x_coords, y_coords, z_coords = zip(*vertices)
    faces = [
        [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
        [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7],
    ]
    i, j, k = zip(*faces)
    return go.Mesh3d(
        x=x_coords, y=y_coords, z=z_coords,
        i=i, j=j, k=k,
        color=color, opacity=0.7,
        hovertext=hovertext, hoverinfo="text"
    )

# Load all data
aircraft_data = load_flight_info(flight_info_path)
injury_map = parse_category_file(injury_path)
damage_map = parse_category_file(damage_path)

# Merge and structure data
records = []
for aircraft, pdfs in aircraft_data.items():
    for pdf in pdfs:
        injury = injury_map.get(pdf, 'Unknown')
        damage = damage_map.get(pdf, 'Unknown')
        records.append({
            'aircraft': aircraft,
            'pdf': pdf,
            'injury': injury,
            'damage': damage
        })

# Aggregate per aircraft
grouped = defaultdict(lambda: {'pdf_count': 0, 'injuries': set(), 'damages': set()})
for rec in records:
    grouped[rec['aircraft']]['pdf_count'] += 1
    grouped[rec['aircraft']]['injuries'].add(rec['injury'])
    grouped[rec['aircraft']]['damages'].add(rec['damage'])

# Layout aircraft in a grid
x_vals, y_vals, z_vals, heights, widths, texts, colors = [], [], [], [], [], [], []
i = 0
spacing = 5
for aircraft, info in grouped.items():
    x = (i % 20) * spacing
    y = (i // 20) * spacing
    z = 0
    height = info['pdf_count']
    injury_level = map_injury_level(info['injuries'])
    damage_level = map_damage_level(info['damages'])

    color = f'rgba({injury_level*60}, 0, 150, 0.7)'  # Darker = worse injury
    text = f"Aircraft: {aircraft}<br>PDFs: {height}<br>Injuries: {', '.join(info['injuries'])}<br>Damage: {', '.join(info['damages'])}"

    x_vals.append(x)
    y_vals.append(y)
    z_vals.append(z)
    heights.append(height)
    widths.append(damage_level)
    colors.append(color)
    texts.append(text)
    i += 1

# Create figure
fig = go.Figure()
for x, y, z, h, w, c, t in zip(x_vals, y_vals, z_vals, heights, widths, colors, texts):
    fig.add_trace(create_bar(x, y, z, w, w, h, c, t))

fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(title="Number of Documents"),
        aspectratio=dict(x=2, y=2, z=0.7)
    ),
    title="Interactive Aircraft Incident Cityscape",
    margin=dict(l=0, r=0, b=0, t=40),
    showlegend=False
)

# Export to HTML
fig.write_html("C:\\Users\\olaye\\Documents\\Aircraft_Incident_Cityscape.html")
print("Visualization saved to: C:\\Users\\olaye\\Documents\\Aircraft_Incident_Cityscape.html")
