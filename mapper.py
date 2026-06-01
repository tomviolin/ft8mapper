import folium
from folium.plugins import FastMarkerCluster
from keplergl import KeplerGl

import pandas as pd
import numpy as np
import maidenhead as mh
import os,sys
from glob import glob
from datetime import datetime
import re

def maidenhead_to_latlon(maidenhead):
    """Convert a Maidenhead grid locator to latitude and longitude."""
    if maidenhead == '':
        return None, None
    try:
        lat, lon = mh.to_location(maidenhead)
        return lat, lon
    except Exception as e:
        print(f"Error converting Maidenhead: {e}")
        return None, None


def read_ft8_file(jt9_ft8_file):
    """Read an FT8 log file and extract relevant information."""
    UTC = datetime.strptime(jt9_ft8_file.split('/')[-1].split('.')[0][-15:], '%Y%m%d_%H%M%S')

    headers = ['UTC','dB','DT','Freq', 'M','Message', 'Maidenhead', 'Latitude', 'Longitude']

    records  = []
    f = open(jt9_ft8_file, 'r').readlines()
    for line in f:
        if line.startswith('<'):
            break
        if line.startswith(' ') or line.startswith('\n'):
            continue
        fields = { headers[0]: line[0:6].strip(),
                   headers[1]: float(line[7:11].strip()),
                   headers[2]: float(line[11:16].strip()), 
                   headers[3]: int(line[16:21].strip()),
                   headers[4]: line[21:24].strip(),
                   headers[5]: line[24:].strip() }
        fields['UTC'] = UTC
        #print(fields)
        message = fields['Message'].split(' ')
        fields['Maidenhead'] = ''
        for msg in message:
            #print(f"Checking message part: {msg}")
            if re.match(r'^[A-Z][A-Z][0-9][0-9]$', msg) is not None and msg != 'RR73':
                #print(f"Found Maidenhead: {msg}")
                fields['Maidenhead'] = msg
                break

        records.append(fields)
        
    df = pd.DataFrame(records, columns=headers)
    if df.empty:
        print(f"No valid records found in file: {jt9_ft8_file}")
        return df
    df['Latitude'], df['Longitude'] = zip(*df['Maidenhead'].apply(maidenhead_to_latlon))
    return df


""" sample log file:
040345   5  0.0 1653 ~  AB7JN KC0FSH R-05                       
040345   0  0.1  759 ~  MW0UPH W9DXP EM76                       
040345 -10 -0.1 2241 ~  KE5YYC KC5JEC DM56                      
040345  -7  0.0 1232 ~  K6LUM WA4TED 73                         
040345  -8  0.0 1806 ~  KB3DQI KG4JOK R+09                      
040345 -10  0.2  894 ~  CQ N4NJJ DM26                           
040345 -10  0.1 1445 ~  5P1KZX KE6XL DM13                       
040345  -5  0.1 1987 ~  CQ VE3BZ FN04                           
040345  -6  0.0 2042 ~  KB9RCA F4LWD -11                        
040345 -10  0.0  825 ~  KC2HGP KD2T RR73                        
040345 -11  0.3 1311 ~  W5AIM K7IOC 73                          
040345  -4  0.0 1592 ~  CQ KF0IPD DM79                          
040345  -4 -0.1 1561 ~  DL5NDD N5WXB RR73                       
040345 -12  0.3 1594 ~  IW9FRA K8USA -11                        
040345 -13  0.0 2068 ~  VE4ZIM VA3THP R-18                      
<DecodeFinished>   0  15        0
"""



"""
    return df
"""
def create_folium_map(df):
    """Create a map with markers for each FT8 contact."""
    m = folium.Map(location=[0, 0], zoom_start=2)
    marker_cluster = FastMarkerCluster().add_to(m)

    for _, row in df.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            popup_text = f"UTC: {row['UTC']}<br>Signal: {row['dB']} dB<br>Frequency: {row['Freq']} MHz<br>Message: {row['Message']}"
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=popup_text
            ).add_to(marker_cluster)

    return m


config = {
    "version": "v1",
    "config": {
        "visState": {
            "layers": [
                {
                    "id": "point_layer", 
                    "type": "point",
                    "config": {
                        "dataId": "data",  # Must match the name used in add_data or init
                        "label": "dB Points",
                        "color": [255, 0, 0], # Fallback color
                        "isVisible": True,
                        "visConfig": {
                            "opacity": 0.8,
                            "radius": 3,
                            "colorRange": {
                                "name": "Ice And Fire", # Built-in palette name
                                "type": "diverging",
                                "category": "Uber",
                                "colors": ["#0099CC", "#FFFFFF", "#FF9900"],
                                "reversed": False
                            }
                        }
                    },
                    "visualChannels": {
                        # THIS IS THE KEY PART: Force color by 'db_value'
                        "colorField": {"name": "dB", "type": "real"},
                        "colorScale": "quantile" # Options: 'quantile', 'linear', 'ordinal'
                    }
                }
            ]
        }
    }
}




def create_keplergl_map(df):


    """Create a Kepler.gl map with markers for each FT8 contact."""
    from keplergl import KeplerGl
    m = KeplerGl(height=900, config=config)
    m.add_data(data=df, name="FT8 Contacts")
    return m



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mapper.py <ft8_log_file>")
        sys.exit(1)
    jt9_ft8_file =  sys.argv[1] # Replace with your FT8 log file path
    files = sorted(glob(jt9_ft8_file))
    if not files:
        print(f"No files found matching: {jt9_ft8_file}")
        sys.exit(1)
    maindf = pd.DataFrame()
    for file in files:
        print(f"Processing file: {file}")
        df = read_ft8_file(file)
        if df.empty:
            print(f"No valid data found in file: {file}")
            continue
        maindf = pd.concat([maindf, df], ignore_index=True)


    ft8_kepler_map = create_keplergl_map(maindf)
    ft8_kepler_map.save_to_html(file_name='ft8_contacts_kepler_map.html')
    print("Kepler map has been saved as ft8_contacts_kepler_map.html")

    ft8_map = create_map(maindf)
    ft8_map.save('ft8_contacts_map.html')
    print("Map has been saved as ft8_contacts_map.html")


