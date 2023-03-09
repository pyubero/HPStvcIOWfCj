import os
import pandas as pd
import geopandas as gpd
from tqdm import tqdm

DIR_OUTPUT = "./callejeros"

# Prepare output data
MUNICIPALITIES = []
STREET_NAMES = []
GEOMETRIES = []

# For every COMUNIDAD AUTONOMA...
_comunidad = "comunidad-de-madrid"
_filepath = os.path.join(DIR_OUTPUT, _comunidad)

# ... load data
df = pd.read_excel(f"{_filepath}_streets.xlsx")
dispdf = df[df["Display"] == 1]
municipios = dispdf["Municipality"].unique()

# For every MUNICIPALITY...
for municipio in tqdm(municipios):

    # ... load municipality data
    _gjson_fp = os.path.join(_filepath, f"{_comunidad}_{municipio}.geojson")
    _gjson = gpd.read_file(_gjson_fp)

    # ... list streets to be displayed on the map
    _mun_df = dispdf[dispdf["Municipality"] == municipio]
    _streets = _mun_df["Street_name"].to_list()

    # For every STREET to de displayed...
    for street in _streets:
        geometry = _gjson[_gjson["Name"] == street]["geometry"].iloc[0]

        # ... append to output
        MUNICIPALITIES.append(municipio)
        STREET_NAMES.append(street)
        GEOMETRIES.append(geometry)

# Save GeoJSON
out_df = pd.DataFrame(
            zip(MUNICIPALITIES, STREET_NAMES),
            columns=["Municipality", "Name"]
            )
out_df = gpd.GeoDataFrame(out_df, geometry=GEOMETRIES)
out_df.to_file("mappable.geojson", driver="GeoJSON")
