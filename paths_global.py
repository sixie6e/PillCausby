import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
import numpy as np

# pd.read_csv('flight_data.csv'))
data = {
    'flight_id': ['N344AP']*5 + ['N77555']*5,
    'lat': [34.05, 36.17, 39.9, 40.71, 43.65, 51.5, 50.85, 48.86, 40.71, 34.05],
    'lon': [-118.24, -115.14, -105.0, -74.00, -79.38, -0.12, 4.35, 2.35, -74.00, -118.24]
}
df = pd.DataFrame(data)

# map
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree()) 
ax.set_extent([-180, 180, -60, 80], crs=ccrs.PlateCarree()) 
ax.add_feature(cfeature.LAND, color='lightgrey')
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
ax.add_feature(cfeature.LAKES, alpha=0.5, facecolor='white')
ax.add_feature(cfeature.RIVERS, alpha=0.5, facecolor='white')

# each flight
for flight_id, group in df.groupby('flight_id'):
    ax.plot(group['lon'], group['lat'], transform=ccrs.Geodetic(), # account for curviture
            label=f'Flight {flight_id}', linewidth=2, alpha=0.6)
    ax.plot(group['lon'].iloc[0], group['lat'].iloc[0], 'go', markersize=5, transform=ccrs.Geodetic())
    ax.plot(group['lon'].iloc[-1], group['lat'].iloc[-1], 'ro', markersize=5, transform=ccrs.Geodetic())

plt.title('Flight Paths for ' + flight_id + ' Past 5 Years')
plt.legend()
plt.savefig('flight_paths.png', dpi=150)
plt.show()
