import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
import numpy as np

# pd.read_csv('flight_data.csv')
data = {
    'flight_id': ['N326VA']*5 + ['N71UM']*5,
    'lat': [34.05, 36.17, 39.9, 40.71, 43.65, 44.75, 45.0, 43.65, 44.3, 44.8], 
    'lon': [-118.24, -115.14, -105.0, -74.00, -79.38, -69.7, -68.8, -70.2, -69.0, -68.7] 
}

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

ax.add_feature(cfeature.LAND, color='lightgrey')
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
ax.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='gray')
ax.add_feature(cfeature.LAKES, alpha=0.5, facecolor='white')
ax.add_feature(cfeature.RIVERS, alpha=0.5, facecolor='white')

for flight_id, group in df_maine.groupby('flight_id'):
    if not group.empty:
        ax.plot(group['lon'], group['lat'], transform=ccrs.Geodetic(), 
                label=f'Flight {flight_id}', linewidth=2, alpha=0.6)
        ax.plot(group['lon'].iloc[0], group['lat'].iloc[0], 'go', markersize=5, transform=ccrs.Geodetic())
        ax.plot(group['lon'].iloc[-1], group['lat'].iloc[-1], 'ro', markersize=5, transform=ccrs.Geodetic())

plt.title('Flight Paths for ' + flight_id)
plt.legend()
plt.savefig('paths_maine.png', dpi=150)
plt.show()
