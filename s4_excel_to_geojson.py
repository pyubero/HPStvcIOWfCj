import os
import pandas as pd
import geopandas as gpd

DIR_OUTPUT = "./callejeros"

# For every COMUNIDAD AUTONOMA
_comunidad = "comunidad-de-madrid"
_filepath = os.path.join(DIR_OUTPUT, _comunidad)

df = pd.read_excel(f"{_filepath}_streets.xlsx")
