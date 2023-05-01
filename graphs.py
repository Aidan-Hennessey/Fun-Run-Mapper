"""
What we need:

glue - takes segments and glues them into a graph

compress - compresses drawing graph by curvature

fundemental_graph - condences all the way down (leaving no degree 2 vertices)

represent - creates a drawing representation that respects the fundemental graph

loss - a measure of loss between the condensed graph and the representation

perturb - perturbs the graph to nearby FG-respecting representation

solve - link everything together in a smart and fast drawing solver

NOTE ON GRAPH REPRESENTATION:
In most cases, graphs are represented as dictionaries mapping from vertices to 
neighboring vertices. Exceptions include the input to glue, which is a list
of lists of points, with the understanding that each list corresponds to a 
path in the natural way (neighboring points in a list are adjacent in graph).
"""

import numpy as np
from scipy.spatial.distance import cdist

from kd_tree import KDTree
from fast_gradient_decent import point_point_dist

GLUE_THRESH = 0.02
STUBBLE_THRESH = 0.04

"""glues paths together into a graph by connecting ends to things if close"""
def glue(paths):
    glued_graph = {}

    # add intra-path connections
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

    # TODO: solve self-intersections

    # add inter-path connections
    for i in range(len(paths)):
        for j in range(i, len(paths)):
            connections = find_intersections(paths[i], paths[j])
            # TODO: add in connections

"""Finds a list of edges that need to be added to glue paths together. Written by chat-GPT."""
def find_intersections(path1, path2, threshold=GLUE_THRESH):
    # TODO: edit first section to use KD-trees
    # Compute pairwise distances between all points in path1 and path2
    distances = cdist(path1, path2)
    
    # Find indices of points where distances are below the threshold
    indices = list(zip(*np.where(distances < threshold)))
    
    # Initialize variables to track which points have been included in an event
    used1 = set()
    used2 = set()
    events = []
    
    for i, j in indices:
        # Skip this index pair if one of the points has already been used in an event
        if i in used1 or j in used2:
            continue
        
        # Add this pair to the list of events
        events.append((path1[i], path2[j]))
        
        # Mark all adjacent points within the threshold distance as used
        for ii in range(i, len(path1)):
            if cdist([path1[ii]], [path2[j]]) < threshold:
                used1.add(ii)
            else:
                break
        
        for jj in range(j, len(path2)):
            if cdist([path1[i]], [path2[jj]]) < threshold:
                used2.add(jj)
            else:
                break
    
    return events

"""Removes hairs with distance < stubble_thresh"""
def shave_stubble(graph, threshold=STUBBLE_THRESH):
    done = False
    while not done:
        points = graph.keys()
        for point in points:
            if len(graph[point] == 1) and hair_length(point, graph) < threshold:
                remove_hair(point, graph)
                break
        else:
            done = True
                
"""Computes the length of the hair with point at its tip"""
def hair_length(tip, graph):
    last_point = tip
    cur_point = graph[tip][0]
    dist = point_point_dist(last_point, cur_point)

    while len(neighbors := graph[cur_point]) == 2:
        if neighbors[0] == last_point:
            next_point = neighbors[1]
        else:
            next_point = neighbors[0]
        dist += point_point_dist(cur_point, next_point)

        # update location
        last_point = cur_point
        cur_point = next_point

    return dist

"""Removes a hair defined by its tip from the graph"""
def remove_hair(tip, graph):
    cur_point = tip

    while len(graph[cur_point]) == 1:
        next_point = graph[cur_point][0]
        
        graph[next_point].remove(cur_point)
        del graph[cur_point]

        # update location
        cur_point = next_point

"""Compresses the drawing representation to one without many edges"""
def compress(graph):
    points = graph.keys()
    done = False
    while not done:
        for point in points:
            if len(neighbors := graph[point]) == 2:
                n1, n2 = neighbors
                if importance(point, n1, n2) < IMPORTANCE_THRESH:
                    graph[n1].remove(point)
                    graph[n1].append(n2)
                    graph[n2].remove(point)
                    graph[n2].append(n1)
                    del graph[point]
                    break
        else:
            done = True
                