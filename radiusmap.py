import folium
import json
from haversine import haversine, Unit
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import os

center_lat = 34.0522
center_lon = -118.2437
radius_miles = 5
kml_namespace = {'kml': 'http://www.opengis.net/kml/2.2'}


def parse(file_path):
    paths = []  
      
    if not os.path.exists(file_path):
        print(f"Error: not found")
        return paths

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        placemarks = root.findall('.//kml:Placemark', kml_namespace)
        
        for placemark in placemarks:
            line_string = placemark.find('kml:LineString', kml_namespace)
            
            if line_string is not None:
                coordinates_tag = line_string.find('gx:coord', kml_namespace)
                
                if coordinates_tag is not None:
                    coord_str = coordinates_tag.text.strip()
                    path = []
                    
                    for lon_lat_alt in coord_str.split():
                        parts = lon_lat_alt.split(',')
                        if len(parts) >= 2:
                            lon = float(parts[0])
                            lat = float(parts[1])
                            path.append((lat, lon))
                    
                    if path:
                        paths.append(path)
                        
    except ET.ParseError as e:
        print(f"Error parsing KML file: {e}")
        
    print(f"Successfully loaded {len(paths)} flight paths.")
    return paths


def flight_map():
    icao_hex = input("ICAO Hex: ").strip().upper()
    kml_file = input("KML file: ").strip()

    try:
        user_lat = float(input("Center Latitude: "))
        user_lon = float(input("Center Longitude: "))
        center_coords = (user_lat, user_lon)
    except ValueError:
        print("\nInvalid latitude/longitude. Using default center coordinates.")
        center_coords = (center_lat, center_lon)

    paths = parse(kml_file)
    
    if not paths:
        print("\nNo flight paths found in the KML file or the file could not be read.")
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
            
            if path:
                folium.CircleMarker(
                    location=path[0],
                    radius=3,
                    color='white',
                    fill=True,
                    fill_color=path_color,
                    tooltip=f"Start: Flight {i+1}"
                ).add_to(group)
                folium.CircleMarker(
                    location=path[-1],
                    radius=3,
                    color='black',
                    fill=True,
                    fill_color=path_color,
                    tooltip=f"End: Flight {i+1}"
                ).add_to(group)

    title_html = f'''
                 <h3 align="center" style="font-size:16px"><b>Flight Paths for ICAO: {icao_hex} within {radius_miles} Miles of ({center_coords[0]:.4f}, {center_coords[1]:.4f})</b></h3>
                 '''
    m.get_root().html.add_child(folium.Element(title_html))
    folium.LayerControl().add_to(m)
    file_name = f"{icao_hex}_map.html"
    m.save(file_name)
    print(f"\nSaved map with {paths} path(s) in range to {file_name}")

if __name__ == "__main__":
    flight_map()
