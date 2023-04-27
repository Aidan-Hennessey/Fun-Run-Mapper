import math
import numpy as np
import sys
import socket
from functools import reduce

from points import read_gps
from edges import read_edges, point_edge_dist
from kd_tree import KDTree
from fast_gradient_decent import gradient_decend, representative_subgraph, \
                                regularized_loss, random_init, edges_as_points
from fast_gradient_decent import gradient_decend, regularized_loss, random_init
from gradient_decent import representative_subgraph

buffer = ""
curr_csock = None

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
    putline(x)
    putline(y)
    putline(theta)
    putline(r)
    putline(gamma)

"""Interface wrapper for gradient_decend"""
def GD_iter():
    points, graph, parameters = read_in_data()
    improved_bundle = gradient_decend(points, graph, parameters)
    write_param_bundle(improved_bundle)

"""Writes a list of edges (aka a subgraph) to stdout"""
def write_edge_list(edges):
    putline(len(edges))
    for edge in edges:
        (a, b), (c, d) = edge
        putline(a, b, c, d)

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
    samples_to_parents = {}
    subgraph_points = edges_as_points(subgraph, samples_to_parents)
    subgraph_tree = KDTree(subgraph_points)
    print(regularized_loss(points, subgraph_tree, samples_to_parents))

"""Interface wrapper for random_init"""
def get_init():
    params = random_init()
    write_param_bundle(params)

"""Takes a line from the current client socket
    NOTE: we assume that the client will never hang without closing connection"""
def getbuffer():
    global curr_csock
    if curr_csock == None:
        raise RuntimeError("client socket is None")

    buffer = curr_csock.recv(1024)
    msg = buffer
    while buffer: # connection ended
        buffer = curr_csock.recv(1024)
        msg += buffer
    return msg.decode('utf-8')

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

def putline(*args):
    global curr_csock
    line = str(args[0]) + reduce(lambda acc,x: acc + ' ' + str(x), args[1:], "") + '\n'
    if curr_csock == None:
        raise RuntimeError("client socket is None")
    return curr_csock.sendall(line.encode('utf-8'))

"""
The REPL the website interacts with
"""
def main(ssock):
    global buffer
    global curr_csock

    while True:
        curr_csock, addr = ssock.accept()
        print('[+] recieved connection from', *addr)
        buffer = getbuffer()

        line = getline()
        if line == "GD_iter":
            GD_iter()
        elif line == "subgraph":
            subgraph()
        elif line == "loss":
            loss()
        elif line == "get_init":
            get_init()
        else:
            print("[-] uh-oh! That's not a recognized function call", file=sys.stderr)

        # client is finished
        more_client_data = curr_csock.recv(1024)
        if more_client_data:
            print(f"[-] bad: client sent extra data: {more_client_data}", file=sys.stderr)

if __name__ == "__main__":
    HOST = ''     # Symbolic name meaning all available interfaces
    PORT = 0  # Arbitrary non-privileged port, 0 will find an open port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ssock:
        ssock.bind((HOST, PORT))
        print(f"[+] listening on port {ssock.getsockname()[1]}")
        ssock.listen()
        main(ssock)
