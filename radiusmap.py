import xml.etree.ElementTree as elementree
import folium
import sys
import os
import requests 

kml_namespace = "{http://www.opengis.net/kml/2.2}"
gx_namespace = "{http://www.google.com/kml/ext/2.2}"

def parse_kml_track(filepath):
    coordinates = []
    try:
        tree = elementree.parse(filepath)
        root = tree.getroot()
       
        coord_elements = root.findall(f".//{gx_namespace}coord")
        
        if coord_elements:
            for coord in coord_elements:
                parts = coord.text.strip().split()
                if len(parts) >= 2:
                    coordinates.append([float(parts[1]), float(parts[0])])
        else:
            ns = {"kml": "http://www.opengis.net/kml/2.2"}
            coords_text = root.findall(".//kml:coordinates", ns)
            for block in coords_text:
                points = block.text.strip().split()
                for p in points:
                    parts = p.split(',')
                    if len(parts) >= 2:
                        coordinates.append([float(parts[1]), float(parts[0])])

        return coordinates
    except Exception as e:
        print(f"Error: {e}")
        return []

def fetch_kml_from_api(identifier):
    '''	
    print(f"Searching API for: {identifier}...")
    return None
    # either opensky or adsb.lol most likely will be used
    '''
    pass
    
def generate_map(coordinates, center_lat, center_lon, diameter_km, output_html="radius_map.html"):
    if not coordinates:
        print("No coordinates.")

    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="OpenStreetMap")

    radius_meters = (diameter_km / 2) * 1000
    folium.Circle(
        location=[center_lat, center_lon],
        radius=radius_meters,
        color="red",
        fill=True,
        fill_opacity=0.1,
        tooltip=f"Diameter(km): {diameter_km}"
    ).add_to(m)

    if coordinates:
        folium.PolyLine(
            locations=coordinates,
            color="blue",
            weight=4,
            opacity=0.7,
            tooltip="Flight Path"
        ).add_to(m)

        folium.Marker(coordinates[0], popup="Start", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(coordinates[-1], popup="End", icon=folium.Icon(color='red')).add_to(m)

    folium.Marker(
        [center_lat, center_lon], 
        popup="Center of Interest", 
        icon=folium.Icon(color='black', icon='crosshairs', prefix='fa')
    ).add_to(m)

    m.save(output_html)
    print("-" * 50)
    print(f"Map saved successfully: {os.path.abspath(output_html)}")

def main(): 
    choice = input("Search by N-Number/ICAO (n) or Load local KML (l)? ").lower()
    path_coordinates = []

    if choice == 'n':
        identifier = input("Enter N-Number or ICAO: ").strip()
        path_coordinates = fetch_kml_from_api(identifier)
        if not path_coordinates:
            print("API not configured. Use local KML file.")
            return
    else:
        kml_file = input("KML file: ").strip()
        path_coordinates = parse_kml_track(kml_file)

    try:
        c_lat = float(input("Center Latitude: "))
        c_lon = float(input("Center Longitude: "))
        diameter = float(input("Diameter(km): "))
    except ValueError:
        print("Invalid.")
        return

    generate_map(path_coordinates, c_lat, c_lon, diameter)

if __name__ == "__main__": 
    main()
