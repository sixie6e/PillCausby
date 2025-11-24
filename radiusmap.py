import requests
import folium
import json
from haversine import haversine, Unit
from datetime import datetime, timedelta
import random

center_lat = 34.0522
center_lon = -118.2437
radius_miles = 5

# replace this with loop to download, extract, and process kml
def get_history(icao_number, years=5):
    print(f"History for ICAO: {icao_number}")
    num_paths = random.randint(5, 15)
    paths = []
    base_lat = center_lat + random.uniform(-0.5, 0.5)
    base_lon = center_lon + random.uniform(-0.5, 0.5)

    for i in range(num_paths):
        path_length = random.randint(20, 50)
        path = []
        current_lat = base_lat + random.uniform(-0.05, 0.05)
        current_lon = base_lon + random.uniform(-0.05, 0.05)
        
        for j in range(path_length):
            current_lat += random.uniform(-0.01, 0.01)
            current_lon += random.uniform(-0.01, 0.01)
            path.append((current_lat, current_lon))
        
        path[0] = (center_lat + random.uniform(-0.2, 0.2), center_lon + random.uniform(-0.2, 0.2))
        path[-1] = (center_lat + random.uniform(-0.2, 0.2), center_lon + random.uniform(-0.2, 0.2))
        paths.append(path)

    print(f"\nSuccess.")
    return paths


def flight_map():
    icao_hex = input("ICAO Hex: ").strip().upper()

    try:
        user_lat = float(input("Center Latitude: "))
        user_lon = float(input("Center Longitude: "))
        center_coords = (user_lat, user_lon)
    except ValueError:
        print("\nInvalid latitude/longitude. Using default center coordinates.")
        center_coords = (center_lat, center_lon)

    paths = get_history(icao_hex)
    
    if not paths:
        print("\nNo flight paths found for this ICAO or the data retrieval failed.")
        return

    m = folium.Map(location=center_coords, zoom_start=12, tiles='cartodbdarkmatter')
    folium.Circle(
        location=center_coords,
        radius=radius_miles * 1609.34, # mi to m
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.15,
        popup=f"{radius_miles} Mile Radius",
        tooltip="Area of Interest"
    ).add_to(m)

    folium.Marker(
        center_coords,
        tooltip="Center of Interest",
        icon=folium.Icon(color='red', icon='fa-bullseye', prefix='fa')
    ).add_to(m)
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    group = folium.FeatureGroup(name="Flight Paths in Area", show=True).add_to(m)
    paths_in_radius_count = 0
    
    for i, path in enumerate(paths):
        path_color = colors[i % len(colors)]
        is_in_radius = False
        for lat, lon in path:
            distance = haversine(center_coords, (lat, lon), unit=Unit.MILES)
            if distance <= radius_miles:
                is_in_radius = True
                break

        if is_in_radius:
            paths_in_radius_count += 1
            folium.PolyLine(
                locations=path,
                color=path_color,
                weight=2.5,
                opacity=0.7,
                tooltip=f"Flight {i+1} (ICAO: {icao_hex})"
            ).add_to(group)

    title_html = f'''
                 <h3 align="center" style="font-size:16px"><b>Flight Paths for ICAO: {icao_hex} within {radius_miles} Miles of ({center_coords[0]:.4f}, {center_coords[1]:.4f})</b></h3>
                 '''
    m.get_root().html.add_child(folium.Element(title_html))
    folium.LayerControl().add_to(m)
    file_name = f"{icao_hex}.html"
    m.save(file_name)
    print(f"\nSaved to {file_name}")

if __name__ == "__main__":
    flight_map()
