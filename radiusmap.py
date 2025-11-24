import folium
from haversine import haversine, Unit
import xml.etree.ElementTree as ET
import os

center_lat = 34.0522 
center_lon = -118.2437
radius_miles = 5

kml_namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
gx_namespace = {'gx': 'http://www.google.com/kml/ext/2.2'}

def parse_kml(file_path):
    paths = []
    
    if not os.path.exists(file_path):
        print(f"Error: KML file not found at '{file_path}'")
        return paths

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        placemarks = root.findall('.//kml:Placemark', kml_namespace)
        
        for placemark in placemarks:
            track = placemark.find('gx:Track', gx_namespace)
            
            if track is not None:
                path = []
                for coord_tag in track.findall('gx:coord', gx_namespace): #[cite: 262]
                    coord_str = coord_tag.text.strip()
                    parts = coord_str.split()
                    
                    if len(parts) >= 2:
                        try:
                            lon = float(parts[0])
                            lat = float(parts[1])
                            path.append((lat, lon))
                        except ValueError:
                            continue
                
                if path:
                    paths.append(path)
                        
    except ET.ParseError as e:
        print(f"Error parsing KML file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    print(f"Successfully loaded {len(paths)} flight path(s) from KML file.")
    return paths


def flight_map():
    icao_hex = 'A1CD2D'
    kml_file_path = 'N215MEavg.kml'

    print(f"Using ICAO: {icao_hex}")
    print(f"Loading data from file: {kml_file_path}")

    try:
        user_lat = float(input("Center Latitude: "))
        user_lon = float(input("Center Longitude: "))
        center_coords = (user_lat, user_lon)
    except ValueError:
        print("\nInvalid latitude/longitude. Using default center coordinates.")
        center_coords = (center_lat, center_lon)

    paths = parse_kml(kml_file_path)
    
    if not paths:
        print("\nNo flight paths found or the file could not be read. Map not generated.")
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
    file_name = f"{icao_hex}_map.html"
    m.save(file_name)
    print(f"\nSaved map with {paths_in_radius_count} path(s) in range to {file_name}")

if __name__ == "__main__":
    flight_map()
