import pandas as pd
from trino.dbapi import connect
from trino.auth import BasicAuthentication
from simplekml import Kml, Color
from datetime import datetime

uname = ''
pw = ''
icao = "a97b82"
start = "2021-01-01"
end = "2026-01-01"
outfile = f"{icao}.kml"

def get_flight_data(icao, start, end):
    print(f"Querying Trino for {icao} from {start} to {end}...")

    conn = connect(
        host="trino.opensky-network.org",
        port=443,
        http_scheme="https",
        auth=BasicAuthentication(uname, pw),
    )

    start_ts = int(pd.to_datetime(start).timestamp())
    end_ts = int(pd.to_datetime(end).timestamp())

    query = f"""
    SELECT 
        time, 
        longitude, 
        latitude, 
        geoaltitude 
    FROM osn.ops.state_vectors_data4
    WHERE icao24 = '{icao}'
      AND time >= {start_ts}
      AND time <= {end_ts}
    ORDER BY time ASC
    """
    
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def export_to_kml(df, icao, output_path):
    kml = Kml(name=f"Flight History: {icao}")
    df['timestamp'] = pd.to_datetime(df['time'], unit='s')
    df = df.sort_values('timestamp')
    df['gap'] = df['timestamp'].diff() > pd.Timedelta(hours=0.5)
    df['flight_id'] = df['gap'].cumsum()

    for fid, group in df.groupby('flight_id'):
        group = group.dropna(subset=['longitude', 'latitude'])
        if group.empty:
            continue

        line = kml.newlinestring(name=f"Flight Segment {fid}")
        coords = []
        for _, row in group.iterrows():
            coords.append((row['longitude'], row['latitude'], row['geoaltitude'] or 0))
        
        line.coords = coords
        line.altitudemode = 'absolute'
        line.style.linestyle.width = 2
        line.style.linestyle.color = Color.changealpha("ff", Color.red)

    kml.save(output_path)
    print(f"Successfully saved {len(df)} points to {output_path}")

data = get_flight_data(icao, start, end)

if data is not None and not data.empty:
    export_to_kml(data, icao, outfile)
else:
    print("Error.")
