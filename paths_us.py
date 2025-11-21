import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
import numpy as np

# pd.read_csv('flight_data.csv')
data = {
    'flight_id': ['N180HL']*5 + ['N800BY']*5,
    'lat': [34.05, 36.17, 39.9, 40.71, 43.65, 51.5, 50.85, 48.86, 40.71, 34.05],
    'lon': [-118.24, -115.14, -105.0, -74.00, -79.38, -0.12, 4.35, 2.35, -74.00, -118.24]
}
'''
# only Maine vars
df = pd.DataFrame(data)
min_lon_me = -71.2
max_lon_me = -66.8
min_lat_me = 43.0
max_lat_me = 47.5

# filter data to include only points within Maine
df_maine = df[(df['lon'] >= min_lon_me) & (df['lon'] <= max_lon_me) &
              (df['lat'] >= min_lat_me) & (df['lat'] <= max_lat_me)]

# map
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree()) 
ax.set_extent([min_lon_me, max_lon_me, min_lat_me, max_lat_me], crs=ccrs.PlateCarree()) 
'''

df = pd.DataFrame(data)
min_lon_us = -125
max_lon_us = -66
min_lat_us = 24
max_lat_us = 50
# only us
df_us = df[(df['lon'] >= min_lon_us) & (df['lon'] <= max_lon_us) &
           (df['lat'] >= min_lat_us) & (df['lat'] <= max_lat_us)]

# map
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree()) 
ax.set_extent([min_lon_us, max_lon_us, min_lat_us, max_lat_us], crs=ccrs.PlateCarree()) 

ax.add_feature(cfeature.LAND, color='lightgrey')
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
ax.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='gray')
ax.add_feature(cfeature.LAKES, alpha=0.5, facecolor='white')
ax.add_feature(cfeature.RIVERS, alpha=0.5, facecolor='white')

# flight paths
for flight_id, group in df_us.groupby('flight_id'):
    if not group.empty: # only plot if in the us
        ax.plot(group['lon'], group['lat'], transform=ccrs.Geodetic(), 
                label=f'Flight {flight_id}', linewidth=2, alpha=0.6)
        ax.plot(group['lon'].iloc[0], group['lat'].iloc[0], 'go', markersize=5, transform=ccrs.Geodetic())
        ax.plot(group['lon'].iloc[-1], group['lat'].iloc[-1], 'ro', markersize=5, transform=ccrs.Geodetic())

plt.title('Flight Paths for ' + flight_id + ' Past 5 Years')
plt.legend()
plt.savefig('flight_paths.png', dpi=150)
plt.show()
