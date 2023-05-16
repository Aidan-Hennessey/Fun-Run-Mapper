from flask import Flask, request
from flask_cors import CORS
import math
import numpy as np
import sys
import socket
from functools import reduce
import pathlib

from libstrava import read_gps
from libstrava import read_edges, point_edge_dist
from libstrava import KDTree
from libstrava import gradient_decend, representative_subgraph, embed, \
                                embedding_loss, random_init, edges_as_points
from libstrava import gradient_decend, regularized_loss, random_init
from libstrava import get_subgraph, graph_from_edges

root = str(pathlib.Path(__file__).parent.parent)

buffer = ""
app = Flask(__name__)
CORS(app)

"""
Reads from stdin a point, graph, and parameter bundle
Returns (points, graph, parameters)
Points is a list of points, which are pairs of ints in draw-box coords
Graph is a list of edges, where each edge is a pair of points
x, y are the gps coords of the box's top-left corner
theta is the angle of roation (counter-clockwise)
r is the GPS degrees spanned by bottom of box to top
gamma is a stretch factor - gamma*r is the span left-to-right of the box
"""
def read_in_data_old_api(lines):
    # get points
    num_points = int(next(lines))
    points = []
    for _ in range(num_points):
        x, y = next(lines).split()
        x, y = float(x), float(y)
        points.append((x, y))

    # get edges
    num_edges = int(next(lines))
    edges = []
    for _ in range(num_edges):
        x1, y1, x2, y2 = next(lines).split()
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        edges.append(((x1, y1), (x2, y2)))

    # get params
    x = float(next(lines))
    y = float(next(lines))
    theta = float(next(lines))
    r = float(next(lines))
    gamma = float(next(lines))

    return points, edges, (x, y, theta, r, gamma)

"""
Reads in a drawing, which will be turned into a list of lists of points,
where each inner list represents a path the user drew. The drawing data
itself looks like a series of inner list strings, where each inner list
string is the length n of the list on a line, then x y on the next n lines

Returns the list of paths
"""
def read_in_data_new_api(lines) -> list[list[tuple[float, float]]]:
    paths = []
    while True:
        try:
            path_len = int(next(lines))
        except StopIteration:
            break
        path = []
        paths.append(path)
        for _ in range(path_len):
            x, y = next(lines).split()
            point = float(x), float(y)
            path.append(point)
    return paths

"""writes a parameter bundle to stdout"""
def write_param_bundle(parameters):
    x, y, theta, r, gamma = parameters
    return f"{x}\n{y}\n{theta}\n{r}\n{gamma}\n"

"""Interface wrapper for gradient_decend"""
def GD_iter(points, graph, parameters):
    improved_bundle = gradient_decend(points, graph, parameters)
    return write_param_bundle(improved_bundle)

"""Writes a list of edges (aka a subgraph) to stdout"""
def write_edge_list(edges):
    string = f"{len(edges)}\n"
    for edge in edges:
        (a, b), (c, d) = edge
        string += f"{a} {b} {c} {d}\n"
    return string

"""Interface wrapper for representative_subgraph"""
def subgraph(points, graph, parameters):
    subg = representative_subgraph(points, graph, parameters)
    return write_edge_list(subg)

def subgraph_new_api(paths):
    graph = graph_from_edges(read_edges(f"{root}/data/edge_list.txt"))
    points_tree = KDTree(list(graph.keys()))
    
    subgraph = list(set(get_subgraph(graph, points_tree, paths)))

"""
interface wrapper for regularized_loss
NOTE: Edges passed should JUST BE THE SUBGRAPH, NOT THE WHOLE GRAPH
"""
def loss(points, graph, parameters):
    return str(embedding_loss(points, graph, parameters))
    # samples_to_parents = {}
    # subgraph_points = edges_as_points(subgraph, samples_to_parents)
    # subgraph_tree = KDTree(subgraph_points)
    # return str(regularized_loss(points, subgraph_tree, samples_to_parents))

"""Interface wrapper for random_init"""
def get_init():
    params = random_init()
    return write_param_bundle(params)

"""Transposes each point - sends (a, b) to (b, a)"""
def flip_points(points):
    flipped_points = []
    for point in points:
        x, y = point
        flipped_points.append((y, x))
    return flipped_points

"""Interface wrapper for embed"""
def embed_points(points, _, parameters):
    points = embed(points, parameters)
    return write_points(points)

"""Converts a set of points to a string to print"""
def write_points(points):
    string = f"{len(points)}\n"
    for point in points:
        x, y = point
        string += f"{x} {y}\n"
    return string

def getline() -> str:
    global buffer
    split_string = buffer.split('\n', 1)

    if len(split_string) == 2:
        line, buffer = split_string
        return line
    else:
        line = split_string[0]
        if line == "":
            print(f"[-] bad: got to end of buffer", file=sys.stderr)
        return line

"""
The route the website interacts with
"""
@app.route('/api', methods=['POST'])
@app.route('/api/v1', methods=['POST'])
def api_v1():
    # we are sending a json with the data as a string in the field 'full_data'
    string = request.form['full_data']
    lines = iter(string.splitlines())
    call = next(lines)

    if call == "GD_iter":
        return GD_iter(*read_in_data_old_api(lines))
    elif call == "subgraph":
        return subgraph(*read_in_data_old_api(lines))
    elif call == "loss":
        return loss(*read_in_data_old_api(lines))
    elif call == "get_init":
        return get_init()
    elif call == "embed_points":
        return embed_points(*read_in_data_old_api(lines))
    else:
        print(f"[-] Error: {call} is not a recognized function call", file=sys.stderr)
        return f"bad request: `{call}` must be GD_iter/subgraph/loss/get_init"

@app.route('/api/v2', methods=['POST'])
def api_v2():
    string = request.form['full_data']
    list_of_lists = read_in_data_new_api(iter(string.splitlines()))
    list_of_edges = subgraph_new_api(list_of_lists)
    return write_edge_list(list_of_edges)

if __name__ == "__main__":
    # cert_files = ('/etc/letsencrypt/live/sky.jason.cash/fullchain.pem', '/etc/letsencrypt/live/sky.jason.cash/privkey.pem')
    # app.run(ssl_context=cert_files, host="0.0.0.0", port=8080)
    app.run(host="0.0.0.0", port=8080)

