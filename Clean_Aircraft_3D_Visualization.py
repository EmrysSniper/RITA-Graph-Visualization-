import plotly.graph_objects as go
import pandas as pd
import json
from collections import defaultdict

# Load your JSON dataset
with open("C:\\Users\\olaye\\Documents\\UARC\\final_extracted_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Prepare the dataframe
df = pd.DataFrame(data)
df['aircraft'] = df['Flight Information'].apply(lambda x: x.get('Aircraft') if isinstance(x, dict) else None)
df['pdf'] = df['File Name']

# Group PDFs by aircraft
aircraft_to_pdfs = defaultdict(list)
for _, row in df.iterrows():
    if row['aircraft'] and row['pdf']:
        aircraft_to_pdfs[row['aircraft']].append(row['pdf'])

# Set up 3D plot
fig = go.Figure()
spacing = 5
grid_width = 20
opacity = 0.3
color = 'rgba(0, 100, 255, 0.7)'

aircraft_list = list(aircraft_to_pdfs.keys())

for idx, aircraft in enumerate(aircraft_list):
    col = idx % grid_width
    row = idx // grid_width
    x = col * spacing
    y = row * spacing
    pdfs = aircraft_to_pdfs[aircraft]
    count = len(pdfs)

    for z in range(count):
        hover_text = f"<b>{aircraft}</b><br>PDF Count: {count}<br><br>Files:<br>" + "<br>".join(pdfs[:20])
        if len(pdfs) > 20:
            hover_text += "<br>...and more"
        fig.add_trace(go.Scatter3d(
            x=[x, x+1, x+1, x, x],
            y=[y, y, y+1, y+1, y],
            z=[z]*5,
            mode='lines',
            line=dict(color=color, width=2),
            opacity=opacity,
            hoverinfo='text',
            text=hover_text
        ))

# Final layout
fig.update_layout(
    title="3D Cityscape of Reports Organized by Aircraft Types",
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(title='Number of PDFs'),
        aspectratio=dict(x=2.2, y=1.8, z=0.7),
        camera=dict(
            eye=dict(x=2.2, y=1.8, z=1.2)
        )
    ),
    margin=dict(l=0, r=0, t=50, b=0),
    showlegend=False
)

# Save to interactive HTML file
output_path = "C:\\Users\\olaye\\Documents\\UARC\\Clean_Aircraft_3D_Visualization.html"
fig.write_html(output_path)
print(f"✅ Visualization saved to: {output_path}")
