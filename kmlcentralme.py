import folium
from fastkml import kml
from shapely.geometry import Point

def kml_plot(kml_filepath):
    def extract_placemarks(features):
        extracted = []
        for feature in features:
            if hasattr(feature, 'geometry') and feature.geometry is not None:
                extracted.append(feature)
            elif hasattr(feature, 'features'):
                extracted.extend(extract_placemarks(feature.features()))
        return extracted
    
    with open(kml_filepath, 'rb') as f:
        doc = f.read()

    k = kml.KML()
    k.from_string(doc)    
    initial_feature_list = list(k.features())
    placemarks = extract_placemarks(initial_feature_list)
    point_placemarks = [
        p for p in placemarks 
        if isinstance(p.geometry, Point)
    ]
    maine_center = [45.3675, -68.9722]
    m = folium.Map(
        location=maine_center, 
        zoom_start=7, 
        tiles='Stamen Terrain'
    )
    
    kml_layer = folium.FeatureGroup(name="KML Coordinates")
    for placemark in point_placemarks:
        lon, lat = placemark.geometry.coords[0][:2]
        #tooltip_text = placemark.name if hasattr(placemark, 'name') and placemark.name else "KML Coordinate"        
        folium.Marker(
            location=[lat, lon], 
            #tooltip=tooltip_text,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(kml_layer)  
    kml_layer.add_to(m)
    folium.LayerControl().add_to(m)
    output_filename = "maine_kml_map.png"
    m.save(output_filename)

kml_plot('N71UMavg.kml')
