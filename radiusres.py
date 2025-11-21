import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

latitude = 
longitude = 
radius_miles = 5
radius_deg = radius_miles / 69.047 
api_key = ""
api_url = ""
years = 5
end_date = datetime.utcnow()
start_date = end_date - timedelta(days=365 * years)

#refer to api docs, different methods of querying history
def get_flight_data(lat, lon, radius, start_date, end_date, api_key, api_url):
    print(f"Attempting to fetch data from {start_date} to {end_date} within {radius_miles} miles...")
    params = {
        'lat_min': lat - radius_deg,
        'lat_max': lat + radius_deg,
        'lon_min': lon - radius_deg,
        'lon_max': lon + radius_deg,
        'start_date': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'end_date': end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'api_key': api_key
    }
    
    # response = requests.get(api_url, params=params)
    # if response.status_code == 200:
    #     data = response.json()
    #     flight_points = [{'lat': point['lat'], 'lon': point['lon']} for flight in data for point in flight['track']]
    #     return flight_points
    # else:
    #     print(f"Failed: {response.status_code}")
    #     return []

    print("arbitrary data for test...")
    import random
    flight_points = []
    for _ in range(1000): # random 1000 data points
        flight_points.append({
            'lat': lat + random.uniform(-radius_deg, radius_deg),
            'lon': lon + random.uniform(-radius_deg, radius_deg)
        })
    return flight_points

flight_data = get_flight_data(latitude, longitude, radius_miles, start_date, end_date, api_key, api_url)

if not flight_data:
    print("exiting, no data...")
    exit()

df = pd.DataFrame(flight_data)
geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
center_point = Point(longitude, latitude)
# UTM zone for Maine, 19N for USA)
gdf_projected = gdf.to_crs(epsg=26919) 
center_point_projected = gpd.GeoSeries([center_point], crs="EPSG:4326").to_crs(epsg=26919)
# 5 mi ~ 8046.72m
buffer = center_point_projected.buffer(8046.72) 
gdf_filtered = gdf_projected[gdf_projected.within(buffer.iloc[0])]

fig, ax = plt.subplots(figsize=(10, 10))
'''
#base map optional
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world.plot(ax=ax, color='white', edgecolor='black')
'''
if not gdf_filtered.empty:
    gdf_filtered.plot(ax=ax, marker='.', color='red', markersize=2, alpha=0.5)
gpd.GeoSeries(center_point_projected).to_crs(epsg=4326).plot(ax=ax, color='blue', marker='o', markersize=50)
gpd.GeoSeries(buffer).to_crs(epsg=4326).plot(ax=ax, color='blue', alpha=0.2)

# map boundaries
ax.set_xlim(longitude - 0.1, longitude + 0.1) # zoom boundary adjust
ax.set_ylim(latitude - 0.1, latitude + 0.1)
ax.set_title(f'Flight paths within {radius_miles} miles of {latitude}, {longitude}')
ax.set_xlabel('longitude')
ax.set_ylabel('latitude')
plt.grid(True)
image_path = 'flightpaths.png'
plt.savefig(image_path)
print(f"Image saved to {image_path}")
plt.show()
