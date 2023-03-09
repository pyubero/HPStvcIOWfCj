# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 16:33:02 2023

@author: Pablo
"""
import os
import numpy as np
import geopandas as gpd
from pyrosm import OSM, get_data
import networkx as nx
import osmnx as ox
from pyrosm.data import sources
from shapely import Polygon
from unidecode import unidecode


# ... optional
from matplotlib import pyplot as plt
from tqdm import tqdm     


def poly_to_shapely(filepath):
    '''
    Reads a .poly file and converts it into a shapely object.
    '''
    coords = []
    with open(filepath, 'r') as file:
        assert file.readline() == "polygon\n"
        assert file.readline() == "1\n"
        for line in file.readlines():
            if "END" in line:
                break

            lon = float(line[:-1].split('\t')[1:][0])
            lat = float(line[:-1].split('\t')[1:][1])
            coords.append([lon, lat])
    return Polygon(shell=coords)


def name_2_street(edges, name: str):
    '''
    From a geoJSON of edges, it extracts all *initial* vertices of
    a street given its name.
    '''
    return edges[edges["name"] == name]["u"].to_list()


def is_sequential(graph, nodes):
    '''
    Checks if wthin a graph, a list of nodes is connected by edges.
    '''
    for jj in range(len(nodes)-1):
        if graph.get_edge_data(nodes[jj+1], nodes[jj]) is None:
            return False
    return True


def street_to_routes(graph, street):
    routes = []
    route = []
    for jj in range(len(street)-2):
        if graph.get_edge_data(street[jj+1], street[jj]) is not None:
            route.append(street[jj])
        else:
            routes.append(route)
            route = []
    route.append(street[jj+1])
    routes.append(route)

    routes = [a for a in routes if len(a) > 1]
    return routes


def normalize_string(string):
    words = [w for w in string.split(' ')]
    words = [w.lower() for w in words]
    words = [unidecode(w) for w in words]
    return ' '.join(words)


def strip_string(string):
    words = [w for w in string.split(' ') if w not in IGNORE_LIST]
    return ' '.join(words)


def connect_to_database(client, db_name, raise_exception=True):
    db_exists = db_name in client.list_database_names()

    if (not db_exists) and raise_exception:
        raise Exception("Sorry, the DB %s does no exist." % db_name) 

    return client[db_name]


def connect_to_collection(database, cl_name, raise_exception=True):
    cl_exists = cl_name in database.list_collection_names()

    if (not cl_exists) and raise_exception:
        raise Exception("Sorry, the collection %s does no exist." % cl_name) 

    return database[cl_name]


def document_in_collection(mycollection, doc_filter):
    return mycollection.count_documents(doc_filter)


def insert_in_collection(mycollection, pmid, references):
    mycollection.insert_one({"_id": pmid, "references": references})
    return


def export_streets(path, municipio, streets):
    mun, com = municipio[:-5].split('_')
    filename = '_'.join([com, mun])+".csv"
    filepath = os.path.join(path, filename)

    with open(filepath, 'w+', encoding="utf-8") as file:
        for street in streets:
            file.write(street+'\n')
    return True


DIR_MUNICIPIOS = "./spain/comunidad-de-madrid/"
DIR_CALLEJEROS = './callejeros/'
FILE_OSM = "./madrid-latest.osm.pbf"
DETERMINANTES = set(["la", "el", "lo", "de", "del", "las", "los"])
TIPOS_VIAS = set(["avenida", "calle", "bulevar", "callejon", "camino",
                  "carretera", "circunvalación", "cordel", "paseo", "plaza",
                  "ronda", "travesia", "tunel", "vereda", "rotonda"])
IGNORE_LIST = list(DETERMINANTES | TIPOS_VIAS)

# for municipio in tqdm( os.listdir(DIR_MUNICIPIOS)[135:] ):    
MUNICIPIO_FILE = "majadahonda_comunidad-de-madrid.poly"
_municipio = MUNICIPIO_FILE.split('_', maxsplit=1)[0]

# Load OSM data
bbox = poly_to_shapely(os.path.join(DIR_MUNICIPIOS, MUNICIPIO_FILE))
osm = OSM(FILE_OSM, bounding_box=bbox)

# Obtain graph
nodes,  edges = osm.get_network(nodes=True, network_type="walking")  # ~2mins
if (nodes is None) or (edges is None):
    print(f"<E> Unmapped city {_municipio}")
    # continue #<<<<<<<<<<<<<<<<<<<<<<<<<<
node_ids = nodes["id"].to_list()

#########
# EXPORT NODES AND EDGES AS GEOJSON
# afterwards load those files instead of OSM

# Apparently I don't need the graph
# graph = osm.to_graph(nodes, edges,  graph_type="networkx")  # ~5mins

if "name" not in edges.columns:
    print(f"<E> No street names found for {_municipio}")
    # continue # <<<<<<<<<<<<<<

# Obtain street names
edge_names = edges["name"].to_list()
edge_names = [a for a in edge_names if a is not None]
edge_names = np.unique(edge_names)
print(len(edge_names))
export_streets(DIR_MUNICIPIOS, MUNICIPIO_FILE, edge_names)
# # Reduce names
# streets_rd = [ strip_string( normalize_string(w)) for w in edge_names]
# _= [ ALL_STREETS.append(street) for street in streets_rd]
# ALL_STREETS = list(np.unique(ALL_STREETS).flatten())
# print(len(ALL_STREETS))


# name = "Avenida Guadarrama"
# street= name_2_street(edges, name)
# routes_st = street_to_routes(graph, street)

# x_ = [nodes[nodes["id"]==nd]["lon"].to_list()[0] for nd in street ]
# y_ = [nodes[nodes["id"]==nd]["lat"].to_list()[0] for nd in street ]
# plt.plot(x_, y_, '.')

# fig, ax = ox.plot_graph_routes(graph, routes_st,
#                      node_size = 0,
#                      orig_dest_size =0,
#                      route_alpha=1,
#                      edge_linewidth=0.5)
from shapely import LineString
street_name = edge_names[10]

PTS = []
A, B = [0, 0], [0, 0]
for jj, row in edges[edges["name"]==street_name].iterrows():
    A = row["geometry"].coords[0]
    B = row["geometry"].coords[1]

    PTS.append(A)

import pandas as pd
df = pd.DataFrame( {"Name" : ["Calle",]})
gdf = gpd.GeoDataFrame(df, geometry=[LineString(PTS),])