"""
What we need:

glue - takes segments and glues them into a graph

condense - condences drawing graph by curvature

fundemental_graph - condences all the way down (leaving no degree 2 vertices)

represent - creates a drawing representation that respects the fundemental graph

loss - a measure of loss between the condensed graph and the representation

perturb - perturbs the graph to nearby FG-respecting representation

solve - link everything together in a smart and fast drawing solver

NOTE ON GRAPH REPRESENTATION:
In most cases, graphs are represented as dictionaries mapping from vertices to 
neighboring vertices. Exceptions include the input to glue, which is a list
of your choosing of lists of points, with the understanding that each list corresponds
to a path in the natural way (neighboring points in a list are adjacent in graph).
"""

import numpy as np

from kd_tree import KDTree

GLUE_THRESH = 0.02

"""glues paths together into a graph by connecting ends to things if close"""
def glue(paths):
    # make our KD-tree to do nearest-neighbor search
    all_points = []
    for path in paths:
        all_points += path
    points_tree = KDTree(all_points)

    # TODO: set up a union-find on the points based on path membership

    glued_graph = {}
    for path in paths:
        last_index = len(path) - 1
        for i, point in enumerate(path):
            # initialize neighbors list
            glued_graph[point] = []

            # add neighbors, keeping edge cases in mind
            if i != 0:
                glued_graph[point].append(path[i-1])
            if i != last_index:
                glued_graph[point].append(path[i+1])

            # gluing time
            if i == 0 or i == last_index:
                neighbors = points_tree.query_radius(point, GLUE_THRESH)
                # next, attach to nearest point in each path if the path has a member in neighbors
                # ^^ that's what we need the union-find for

                # also attach to opposite if within thresh