import plotly.graph_objects as go

import networkx as nx

def make_edge(x, y, text, width):
    
    '''Creates a scatter trace for the edge between x's and y's with given width

    Parameters
    ----------
    x    : a tuple of the endpoints' x-coordinates in the form, tuple([x0, x1, None])
    
    y    : a tuple of the endpoints' y-coordinates in the form, tuple([y0, y1, None])
    
    width: the width of the line

    Returns
    -------
    An edge trace that goes between x0 and x1 with specified width.
    '''
    return  go.Scatter(x         = x,
                       y         = y,
                       line      = dict(width = width,
                                   color = 'cornflowerblue'),
                       hoverinfo = 'text',
                       text      = ([text]),
                       mode      = 'lines')



def plot_network(graph, pos, edge_attrs, node_attrs):
    G = graph

    #create edge trace
    edge_trace = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]

        x_pos = [x0, x1, None]
        y_pos = [y0, y1, None]
        
        num_interaction = edge_attrs[str((edge[0], edge[1]))]
        text = edge[0] + "-" + edge[1] 

        trace = make_edge(x_pos, y_pos, text, num_interaction * 100 + 1)
        edge_trace.append(trace)


    #create node trace
    node_trace = go.Scatter(x         = [],
                            y         = [],
                            text      = [],
                            hovertext = [],
                            textposition = "top center",
                            textfont_size = 20,
                            mode      = 'markers+text',
                            marker    = dict(color = [],
                                            size  = [],
                                            line  = None))


    # verified = nx.get_node_attributes(G, "verified").values()
    # verified = list(map(lambda x: "verified" if x else "not verified", verified))
    # follower_count = nx.get_node_attributes(G, "#friends").values()
    # attrs = zip(verified,follower_count)

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)
        color = "cornflowerblue" if node_attrs[node]["verified"] else "green"
        size  = node_attrs[node]["scaled_friends"] * 60 + 10
        # print(size)
        # node_trace["marker"]["size"] = node_attrs[node]["#friends"] + 10
        # node_trace["marker"]["size"] =  10
        verified = "verified" if node_attrs[node]["verified"] else "not verified"
        text = f"{node}\n {verified} \n #followers: {node_attrs[node]['#friends']}"
        node_trace["marker"]["color"] += (color,)
        node_trace["marker"]["size"] += (size,)
        print(node_trace["marker"])
        node_trace['hovertext'] += (text,)
        node_trace['text'] += (node,)

    # node_trace = go.Scatter(
    #     x=node_x, y=node_y,
    #     mode='markers',
    #     hoverinfo='text',
    #     hoverlabel=dict(font=dict(family='sans-serif', size=25)),
    #     marker=dict(
    #         showscale=True,
    #         # colorscale options
    #         #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
    #         #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
    #         #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
    #         colorscale='YlGnBu',
    #         reversescale=True,
    #         color=[],
    #         size=10,
    #         colorbar=dict(
    #             thickness=15,
    #             title='Node Connections',
    #             xanchor='left',
    #             titleside='right'
    #         ),
    #         line_width=2))
    # node_adjacencies = []
    # node_text = []
    # for node, adjacencies in enumerate(attrs):
    #     node_adjacencies.append(adjacencies[1]/1000)
        
    #     node_text.append(adjacencies[0])

    # node_trace.marker.size = node_adjacencies
    # node_trace.text = node_text

    fig = go.Figure(layout=go.Layout(
                    title='<br>Title Here',
                    # titlefont_size=16,
                    autosize=True,
                    showlegend=False,
                    hovermode='closest',
                    # margin=dict(b=20,l=5,r=5,t=40),
                    # annotations=[ dict(
                    #     text="annotation here",
                    #     showarrow=False,
                    #     xref="paper", yref="paper",
                    #     x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    for trace in edge_trace:
        fig.add_trace(trace)
    fig.add_trace(node_trace)
    fig.show()
