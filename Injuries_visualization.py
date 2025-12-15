import plotly.graph_objects as go

# Path to the aircraft names file
file_path = "C:\\Users\\olaye\\Documents\\UARC\\Injuries.txt"

# Step 1: Parse aircraft names and PDFs
def load_aircraft_data(file_path):
    aircraft_data = {}
    current_aircraft = None
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if not line.endswith('.pdf'):
                current_aircraft = line.rstrip(':')
                aircraft_data[current_aircraft] = []
            else:
                aircraft_data[current_aircraft].append(line)
    return aircraft_data

# Step 2: Create 3D bar blocks
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
        color=color, opacity=0.85,
        hovertext=hovertext,
        hoverinfo="text"
    )

# Step 3: Generate and render figure
def generate_visualization(aircraft_data):
    fig = go.Figure()
    spacing = 5

    for idx, (aircraft, pdfs) in enumerate(aircraft_data.items()):
        x = (idx % 20) * spacing
        y = (idx // 20) * spacing
        z = 0
        dx = dy = 1.8  # Size of cube base
        dz = len(pdfs)  # Height = number of PDFs

        color = 'rgba(255, 165, 0, 0.8)'
        hover_text = f"<b>{aircraft}</b><br>PDF Count: {dz}<br><br>PDF Files:<br>" + "<br>".join(pdfs)

        fig.add_trace(create_bar(x, y, z, dx, dy, dz, color, hover_text))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(title='Number of PDFs'),
            aspectratio=dict(x=2, y=2, z=0.7)
        ),
        title="Interactive Aircraft PDF Visualization",
        margin=dict(l=0, r=0, b=0, t=40),
        showlegend=False
    )

    output_path = "C:\\Users\\olaye\\Documents\\UARC\\Imjuries_3D_Bar_With_PDFs.html"
    fig.write_html(output_path)
    print(f"✅ Visualization saved to: {output_path}")

# Run it
aircraft_data = load_aircraft_data(file_path)
generate_visualization(aircraft_data)
