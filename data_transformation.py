import pandas 
import plotly.graph_objects as go
import networkx as nx
import json
from plotting import plot_network
from pathlib import Path


def scale_dict_values(in_dict):
    
    values = in_dict.values()
    min_ = min(values)
    max_ = max(values)

    out_dict = {key: ((v - min_ ) / (max_ - min_) )  for (key, v) in in_dict.items() }

    return out_dict

data_path = Path("Data/2022-09-24_20-27")

def plot(data_path : Path):

    edge_df = pandas.read_csv(data_path / "edge_list.csv", header= None)
    # user_info_df = pandas.read_csv("user_info.csv")

    with open(data_path / "edge_list.json", "r") as handle:
        edges = json.load(handle)

    with open(data_path / "edge_attributes.json", "r") as handle:
        edge_attributes = json.load(handle)

    with open(data_path / "user_attributes.json", "r") as handle:
        user_attributes = json.load(handle)


    user_follower_dict = {}
    for user in user_attributes.keys():
        user_follower_dict[user] = user_attributes[user]["#friends"]

    scaled_follower_dict = scale_dict_values(user_follower_dict)
    for key, value in scaled_follower_dict.items():
        user_attributes[key]["scaled_friends"] = value
    scaled_edge_attributes = scale_dict_values(edge_attributes)


    g = nx.from_pandas_edgelist(df = edge_df, source = 0, target = 1) 
    nx.set_node_attributes(g, user_attributes) 
    pos = nx.spring_layout(g)

    plot_network(g, pos, scaled_edge_attributes, user_attributes)


