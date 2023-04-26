import math
import numpy as np
import sys

from points import read_gps
from edges import read_edges, point_edge_dist
from gradient_decent import gradient_decend, representative_subgraph, regularized_loss, random_init

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
    num_points = int(input())
    points = []
    for _ in range(num_points):
        x, y = input().split()
        x, y = float(x), float(y)
        points.append((x, y))

    # get edges
    num_edges = int(input())
    edges = []
    for _ in range(num_edges):
        x1, y1, x2, y2 = input().split()
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        edges.append(((x1, y1), (x2, y2)))

    # get params
    x = float(input())
    y = float(input())
    theta = float(input())
    r = float(input())
    gamma = float(input())

    return points, edges, (x, y, theta, r, gamma)
    

"""writes a parameter bundle to stdout"""
def write_param_bundle(parameters):
    x, y, theta, r, gamma = parameters
    print(x)
    print(y)
    print(theta)
    print(r)
    print(gamma)

"""Interface wrapper for gradient_decend"""
def GD_iter():
    points, graph, parameters = read_in_data()
    improved_bundle = gradient_decend(points, graph, parameters)
    write_param_bundle(improved_bundle)

"""Writes a list of edges (aka a subgraph) to stdout"""
def write_edge_list(edges):
    print(len(edges))
    for edge in edges:
        (a, b), (c, d) = edge
        print(a, " ", b, " ", c, " ", d)

"""Interface wrapper for representative_subgraph"""
def subgraph():
    points, graph, parameters = read_in_data()
    subg = representative_subgraph(points, graph, parameters)
    write_edge_list(subg)

"""
interface wrapper for regularized_loss
NOTE: Edges passed should JUST BE THE SUBGRAPH, NOT THE WHOLE GRAPH
"""
def loss():
    points, subgraph, parameters = read_in_data()
    print(regularized_loss(points, subgraph, parameters))

"""Interface wrapper for random_init"""
def get_init():
    params = random_init()
    write_param_bundle(params)

"""
The REPL the website interacts with
"""
def REPL():
    while True:
        line = input()
        if line == "GD_iter":
            GD_iter()
        elif line == "subgraph":
            subgraph()
        elif line == "loss":
            loss()
        elif "get_init":
            get_init()
        else:
            print("uh-oh! That's not a recognized function call", file=sys.stderr)
