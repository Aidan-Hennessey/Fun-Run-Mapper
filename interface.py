from flask import Flask, request
from flask_cors import CORS
import math
import numpy as np
import sys
import socket
from functools import reduce

from points import read_gps
from edges import read_edges, point_edge_dist
from kd_tree import KDTree
from fast_gradient_decent import gradient_decend, representative_subgraph, embed, \
                                embedding_loss, random_init, edges_as_points
from fast_gradient_decent import gradient_decend, regularized_loss, random_init
from gradient_decent import representative_subgraph

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
def read_in_data():
    # get points
    num_points = int(getline())
    points = []
    for _ in range(num_points):
        x, y = getline().split()
        x, y = float(x), float(y)
        points.append((x, y))

    # get edges
    num_edges = int(getline())
    edges = []
    for _ in range(num_edges):
        x1, y1, x2, y2 = getline().split()
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        edges.append(((x1, y1), (x2, y2)))

    # get params
    x = float(getline())
    y = float(getline())
    theta = float(getline())
    r = float(getline())
    gamma = float(getline())

    return points, edges, (x, y, theta, r, gamma)


"""writes a parameter bundle to stdout"""
def write_param_bundle(parameters):
    x, y, theta, r, gamma = parameters
    return f"{x}\n{y}\n{theta}\n{r}\n{gamma}\n"

"""Interface wrapper for gradient_decend"""
def GD_iter():
    points, graph, parameters = read_in_data()
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
def subgraph():
    points, graph, parameters = read_in_data()
    subg = representative_subgraph(points, graph, parameters)
    return write_edge_list(subg)

"""
interface wrapper for regularized_loss
NOTE: Edges passed should JUST BE THE SUBGRAPH, NOT THE WHOLE GRAPH
"""
def loss():
    points, graph, parameters = read_in_data()
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
def embed_points():
    points, _, parameters = read_in_data()
    points = embed(points, parameters)
    return write_points(points)

"""Converts a set of points to a string to print"""
def write_points(points):
    string = f"{len(points)}\n"
    for point in points:
        x, y = point
        string += f"{x} {y}\n"
    return string

def getline():
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
@app.route('/', methods=['POST'])
def main():
    global buffer
    # we are sending a json with the data as a string in the field 'full_data'
    buffer = request.form['full_data']

    line = getline()
    if line == "GD_iter":
        return GD_iter()
    elif line == "subgraph":
        return subgraph()
    elif line == "loss":
        return loss()
    elif line == "get_init":
        return get_init()
    elif line == "embed_points":
        return embed_points()
    else:
        print(f"[-] Error: {line} is not a recognized function call", file=sys.stderr)
        return f"bad request: `{line}` must be GD_iter/subgraph/loss/get_init"

if __name__ == "__main__":
    app.run(threaded=False)
