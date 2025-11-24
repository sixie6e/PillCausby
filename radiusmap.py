import xml.etree.ElementTree as elementree
import folium
import sys
import os

kml_namespace = "{http://www.opengis.net/kml/2.2}"
gx_namespace = "{http://www.google.com/kml/ext/2.2}"

def parse_kml_track(filepath):
    coordinates = []
    try:
        elementree.register_namespace('', 'http://www.opengis.net/kml/2.2')
        elementree.register_namespace('gx', 'http://www.google.com/kml/ext/2.2')

        tree = elementree.parse(filepath)
        root = tree.getroot()
        
        coord_elements = root.findall(f".//{gx_namespace}coord")

        if not coord_elements:
            print(f"Error: No <gx:coord> elements found in {filepath}")
            return []

        print(f"Found {len(coord_elements)} track points.")

        for coord in coord_elements:
            parts = coord.text.strip().split()
            if len(parts) >= 2:
                try:
                    lon = float(parts[0])
                    lat = float(parts[1])
                    coordinates.append([lat, lon])
                except ValueError:
                    print(f"Parse error: {coord.text}")
                    continue

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        sys.exit(1)

    return coordinates

def flight_path(coordinates, center_lat, center_lon, output_html="kml_map.html"):

    if not coordinates:
        print("Empty path.")
        return

    m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles="OpenStreetMap")

    folium.PolyLine(
        locations=coordinates,
        color="blue",
        weight=4,
        opacity=0.8,
        tooltip="KML Data"
    ).add_to(m)
    start_point = coordinates[0]
    end_point = coordinates[-1]

    folium.Marker(
        location=start_point,
        popup=f"Start: ({start_point[0]:.4f}, {start_point[1]:.4f})",
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(m)

    folium.Marker(
        location=end_point,
        popup=f"End: ({end_point[0]:.4f}, {end_point[1]:.4f})",
        icon=folium.Icon(color='red', icon='stop', prefix='fa')
    ).add_to(m)
    
    m.save(output_html)
    print("-" * 50)
    print(f"Map saved to: {os.path.abspath(output_html)}")


def main(): 
    print("--- Path Plotter ---")
    kml_file = input(f"KML file: ").strip()

    while True:
        try:
            center_lat = float(input("Center Latitude: "))
            center_lon = float(input("Center Longitude: "))
            break
        except ValueError:
            print("Invalid input.")

    path_coordinates = parse_kml_track(kml_file)

    if path_coordinates:
        flight_path(path_coordinates, center_lat, center_lon)

if __name__ == "__main__": 
    main()
