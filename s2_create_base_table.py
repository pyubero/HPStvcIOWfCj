import os
import pandas as pd
import geopandas as gpd
from tqdm import tqdm


def add_row(dataframe, new_row):
    '''
    Adds a row to an existing dataframe.
    '''
    return pd.concat(
                [dataframe, pd.DataFrame(new_row, columns=dataframe.columns)],
                ignore_index=True
                )


def extract_coords(dataframe):
    lon, lat = [], []
    for elem in dataframe["geometry"].to_list():
        _lon, _lat = elem.coords[0]
        lon.append(_lon)
        lat.append(_lat)
    return lon, lat


def normalize_string(string):
    '''
    Normalizes a string by lowering all letters, and removing any accent.
    '''
    from unidecode import unidecode
    words = [w for w in string.split(' ')]
    words = [w.lower() for w in words]
    words = [unidecode(w) for w in words]
    return ' '.join(words)


def strip_string(string):
    '''
    Strips a string from certain words in the ignore_list.
    '''
    DETERMINANTES = set(["la", "el", "lo", "de", "del", "las", "los"])
    TIPOS_VIAS = set(["avenida", "calle", "bulevar", "callejon", "camino",
                      "carretera", "circunvalación", "cordel", "paseo",
                      "plaza", "ronda", "travesia", "tunel", "vereda",
                      "rotonda"])
    IGNORE_LIST = list(DETERMINANTES | TIPOS_VIAS)

    words = [w for w in string.split(' ') if w not in IGNORE_LIST]
    return ' '.join(words)


DIR_OUTPUT = "./callejeros"
DF = pd.DataFrame(columns=["Display",
                           "Municipality",
                           "Street_name",
                           "Longitude",
                           "Latitude",
                           "Comment"
                           ])

# For every COMUNIDAD AUTONOMA
_comunidad = "comunidad-de-madrid"
_filepath = os.path.join(DIR_OUTPUT, _comunidad)

# For every MUNICIPALITY in _filepath
for file in tqdm(os.listdir(_filepath)):
    _municipality = file.split("_")[-1].split('.')[0]

    data = gpd.read_file(os.path.join(_filepath, file))
    streets = data["Name"].to_list()
    coords = extract_coords(data)
    municip = [_municipality for _ in range(len(streets))]
    comments = ["" for _ in range(len(streets))]
    display = ["0" for _ in range(len(streets))]

    zipped_data = zip(display,
                      municip,
                      streets,
                      coords[0],
                      coords[1],
                      comments
                      )

    DF = add_row(DF, zipped_data)

_output = os.path.join(DIR_OUTPUT, f"{_comunidad}_streets.xlsx")
DF.to_excel(_output, index=False)
