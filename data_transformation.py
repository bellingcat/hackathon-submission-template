import pandas 
import plotly.graph_objects as go
import networkx as nx
import json
from copy_and_paste_is_great import plot_graph

edge_df = pandas.read_csv("edge_list.csv", header= None)

info_df = pandas.read_csv("user_info.csv")
with open("user_info.json", "r") as handle:
    info_dict = json.load(handle)

info_df.dropna(axis=0)

edge_df.dropna(axis=0)


g = nx.from_pandas_edgelist(df = edge_df, source = 0, target = 1) 
nx.set_node_attributes(g, info_dict) 
pos = nx.spring_layout(g)

plot_graph(g, pos)
# TODO  calculate weights and add them to the edge_df where we have the number of interactions in col 2

# G = nx.from_pandas_edgelist(df = edge_df,
#                             source = 0,
#                             target = 1,
#                             edge_attr = 2)


