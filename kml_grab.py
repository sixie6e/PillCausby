import pandas as pd
from traffic.data import opensky
from simplekml import Kml, Color
from datetime import datetime, timedelta

icao = "a97b82" 
start = "2021-01-01"
end = "2026-01-01"
outfile = f"{icao}.kml"

def get_flight_data(icao, start, end):
    print(f"Fetching data for {icao} from {start} to {end}...")
    
    try:
        flight_data = opensky.history(
            start=start,
            stop=end,
            icao=icao,
            return_type="pandas"
        )
        return flight_data
    except Exception as e:
        print(f"Error: {e}")
        return None

def export_to_kml(df, output_path):
    kml = Kml(name=f"Flight History: {icao}")
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df.sort_values('timestamp')
    df['gap'] = df['timestamp'].diff() > pd.Timedelta(hours=.5)
    df['flight_id'] = df['gap'].cumsum()

    for fid, group in df.groupby('flight_id'):
        line = kml.newlinestring(name=f"Flight {fid}")
        coords = []
        for _, row in group.iterrows():
            if pd.notnull(row['longitude']) and pd.notnull(row['latitude']):
                coords.append((row['longitude'], row['latitude'], row['geoaltitude'] or 0))
        line.coords = coords
        line.altitudemode = 'absolute'
        line.style.linestyle.width = 2
        line.style.linestyle.color = Color.changealpha("ff", Color.red)

    kml.save(output_path)
    print(f"Successfully saved to {output_path}")

data = get_flight_data(icao, start, end)
if data is not None and not data.empty:
    export_to_kml(data, outfile)
else:
    print("Error")
