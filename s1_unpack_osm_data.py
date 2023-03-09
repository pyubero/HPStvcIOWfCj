import os
import numpy as np
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
from pyrosm import OSM
from shapely import Polygon, LineString


def poly_to_shapely(filepath):
    '''
    Reads a .poly file and converts it into a shapely object.
    '''
    coords = []
    with open(filepath, 'r', encoding="utf-8") as file:
        assert file.readline() == "polygon\n"
        assert file.readline() == "1\n"
        for line in file.readlines():
            if "END" in line:
                break

            lon = float(line[:-1].split('\t')[1:][0])
            lat = float(line[:-1].split('\t')[1:][1])
            coords.append([lon, lat])
    return Polygon(shell=coords)


def validate_network(nodes, edges):
    '''
    Validates a network and checks that:
        - the region has been mapped and neither nodes, nor edges are None
        - the edges has a "name" column
    '''
    # Check whether the municipio has been mapped
    if (nodes is None) or (edges is None):
        print(f"<E> Unmapped city {_municipio}")
        return False

    # Check whether the municipio has valid street names
    if "name" not in edges.columns:
        print(f"<E> No street names found for {_municipio}")
        return False

    return True


def get_unique_streets(edges):
    '''
    Returns the list of street names from an edges geoDataFrame.
    '''
    edge_names = edges["name"].to_list()
    edge_names = [a for a in edge_names if a is not None]
    return np.unique(edge_names)


def get_routes(graph, nodes):
    '''
    From a list of (supposedly) consecutive nodes, it generates a list
    of lists of REALLY consecutive nodes. Often times streets are not a
    continuous LineString but rather it has some extra "legs".  This function
    aims at identifying those "extra legs".
    '''
    routes = []
    route = []
    for node_idx in range(len(nodes)-2):
        if graph.get_edge_data(nodes[node_idx+1], nodes[node_idx]) is not None:
            route.append(nodes[node_idx])
        else:
            routes.append(route)
            route = []
    route.append(nodes[node_idx+1])
    routes.append(route)

    routes = [a for a in routes if len(a) > 1]
    return routes


def gdf_to_linestring(gdf):
    '''
    Usually, for a specific street the geoDataFrame contains many entries each
    with pairs of shapely Points(). This function gathers all these points
    together into a LineString().
    '''
    if len(gdf) == 0:
        return LineString()

    points = []
    point_a, point_b = [0, 0], [0, 0]
    for _, row in gdf.iterrows():
        point_a = row["geometry"].coords[0]
        point_b = row["geometry"].coords[1]

        points.append(point_a)
    points.append(point_b)
    return LineString(points)


# For every spanish region...
# Visit to download data https://download.geofabrik.de/europe/spain.html
FILE_OSM = "./madrid-latest.osm.pbf"
DIR_MUNICIPIOS = "./spain/comunidad-de-madrid/"
DIR_OUTPUT = "./callejeros"

# For every spanish municipality...
# Download municipalities from https://github.com/JamesChevalier/cities
for _municipio_file in tqdm(os.listdir(DIR_MUNICIPIOS)[:]):
    # _municipio_file = "majadahonda_comunidad-de-madrid.poly"
    _municipio = _municipio_file.split('_', maxsplit=1)[0]

    # Load OSM data
    _bbox = poly_to_shapely(os.path.join(DIR_MUNICIPIOS, _municipio_file))
    osm = OSM(FILE_OSM, bounding_box=_bbox)

    # Obtain graph ~2mins
    _nodes,  _edges = osm.get_network(nodes=True, network_type="walking")
    if not validate_network(_nodes, _edges):
        continue

    # Prepare output data
    STREETS = get_unique_streets(_edges)
    GEOMETRIES = []

    # Extract LineStrings()
    for street in STREETS:
        geometry = gdf_to_linestring(_edges[_edges["name"] == street])
        GEOMETRIES.append(geometry)

    # Prepare output data
    df = pd.DataFrame({"Name": STREETS, })
    df = gpd.GeoDataFrame(df, geometry=GEOMETRIES)

    # Export GeoJSON
    mun, com = _municipio_file[:-5].split('_')
    fpath = os.path.join(
        f"{DIR_OUTPUT}/{com}",
        '_'.join([com, mun])+".geojson"
        )
    df.to_file(fpath, driver="GeoJSON")
