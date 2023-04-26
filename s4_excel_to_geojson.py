'''
Layer labels:
-1: requires manual verification
0 : do not display
1 : display as fully involved (e.g conquistadores)
2 : display as doubtful contribution
'''
import os
import pandas as pd
import geopandas as gpd
from tqdm import tqdm

DIR_OUTPUT = "./callejeros"

# Prepare output data
MUNICIPALITIES = []
STREET_NAMES = []
GEOMETRIES = []
DISPLAYLAYERS = []

# For every COMUNIDAD AUTONOMA...
_comunidad = "comunidad-de-madrid"
_filepath = os.path.join(DIR_OUTPUT, _comunidad)

# ... load data
df = pd.read_excel(f"{_filepath}_streets.xlsx")
dispdf = df[df["DisplayLayer"] != 0]
municipios = dispdf["Municipality"].unique()

# For every MUNICIPALITY...
for municipio in tqdm(municipios):

    # ... load municipality data
    _gjson_fp = os.path.join(_filepath, f"{_comunidad}_{municipio}.geojson")
    _gjson = gpd.read_file(_gjson_fp)

    # ... list streets to be displayed on the map
    _mun_df = dispdf[dispdf["Municipality"] == municipio]
    _streets = _mun_df["StreetName"].to_list()

    # For every STREET to de displayed...
    for street in _streets:
        geometry = _gjson[_gjson["Name"] == street]["geometry"].iloc[0]
        displaylayer = _mun_df[_mun_df["StreetName"] == street]["DisplayLayer"].iloc[0]

        # ... append to output
        MUNICIPALITIES.append(municipio)
        STREET_NAMES.append(street)
        GEOMETRIES.append(geometry)
        DISPLAYLAYERS.append(displaylayer)

# Save GeoJSON
out_df = pd.DataFrame(
            zip(MUNICIPALITIES, STREET_NAMES, DISPLAYLAYERS),
            columns=["Municipality", "Name", "DisplayLayer"]
            )
out_df = gpd.GeoDataFrame(out_df, geometry=GEOMETRIES)
out_df.to_file("mappable.geojson", driver="GeoJSON")
