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
import math
import numpy as np
from random import shuffle

from kd_tree import KDTree
from fast_gradient_decent import point_point_dist

GLUE_THRESH = 0.02
STUBBLE_THRESH = 0.04
IMPORTANCE_THRESH = 0.001
ANGLE_WEIGHT = 2

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

    # glue
    for i in range(len(paths)):
        for j in range(i, len(paths)):
            connections = find_intersections(paths[i], paths[j])
            if i == j:
                remove_self_matches(connections)

            for con_i, con_j in connections:
                do_the_glue(glued_graph, paths[i], paths[j], con_i, con_j)

"""
Glues paths 1 and 2 together using the points at indices i and j
Mutates graph. Returns nothing.
"""
def do_the_glue(graph, path1, path2, i, j):
    p1 = path1[i]
    p2 = path2[j]

    # if i or j is endpoint of path, just connect it onto other path
    if i*j == 0 or i == len(path1) - 1 or j == len(path2) - 1:
        graph[p1].append(p2)
        graph[p2].append(p1)
    else: # stick i in between j and its neighbor
        neighbor = path2[j-1]
        graph[neighbor].remove(p2)
        graph[neighbor].append(p1)
        graph[p2].remove(neighbor)
        graph[p2].append(p1)
        graph[p1].append[p2]
        graph[p1].append[neighbor]

"""Returns a list of pairs of indices at which some gluing should occur"""                
def find_intersections(path1, path2, path2KDtree, point2index):
    intersections = []

    # add every pair within thresh
    for i, p1 in enumerate(path1):
        matches = path2KDtree.query_radius(p1, GLUE_THRESH)
        for match in matches:
            intersections.append((i, point2index[match]))
    
    # replace them all with their corresponding local minima and remove dupes
    intersections = list(set(map(lambda intrscn: local_min_match(path1, path2, intrscn[0], intrscn[1]), intersections)))

    # remove inferior clones
    while remove_clone(path1, path2, intersections): # remove_clone returns true when it removes a clone, false when none left
        pass

    return intersections

"""Given a pair of paths and indices into them, decends to a local optimum, where closer is more optimal"""
def local_min_match(path1, path2, index1, index2):
    def local_min_rec(i, j):
        cur_dist = point_point_dist(path1[i], path2[j])
        if i != len(path1) - 1 and \
                point_point_dist(path1[i + 1], path2[j]) < cur_dist:
            local_min_rec(i + 1, j)
        if i != 0 and \
                point_point_dist(path1[i - 1], path2[j]) < cur_dist:
            local_min_rec(i - 1, j)
        if j != len(path2) - 1 and \
                point_point_dist(path1[i], path2[j + 1]) < cur_dist:
            local_min_rec(i, j + 1)
        if j != 0 and \
                point_point_dist(path1[i], path2[j - 1]) < cur_dist:
            local_min_rec(i, j - 1)

        return i, j
    
    return local_min_rec(index1, index2)

"""
Searches pairwise until it finds a clone. Removes the worse clone and returns true.
If no clone is found after searching all pairs, returns false.
NOTE: The main behavior of this function is to MUTATE the passed intersections list,
not return a slightly different copy

Params:
    path1, path2 - the two paths we're trying to glue together
    intersections - a list of intersections (2tuples of indices) to remove clones from
Returns:
    a boolean - true if clone removed, false if no clones found
"""
def remove_clone(path1, path2, intersections):
    for i, intersection1 in enumerate(intersections):
        for intersection2 in intersections[i+1:]:
            if clones(path1, path2, intersection1, intersection2):
                if first_intersection_better(path1, path2, intersection1, intersection2):
                    intersections.remove(intersection2)
                else:
                    intersections.remove(intersection1)
                return True
    return False

"""
Determines whether 2 pairs of points are "clones" in the sense that you can
obtain one from the other by incrementing indices without ever making the distance
larger than GLUE_THRESH

NOTE: The correctness of this implementation relies on convexity of clone blobs,
which may not be valid. Even if wrong in certain pathalogical cases, should be good
enough

Params:
    path1, path2 - the two paths on which the pairs lie
    intersection1 - tuple of indices into each path of the first pair
    intersection2 - same as intersection1 but second pair
Returns:
    boolean - true if clones, false if distinct
"""
def clones(path1, path2, intersection1, intersection2):
    i1, j1 = intersection1
    i2, j2 = intersection2
    while True:
        iinc = math.copysign(1, i1 - i2)
        jinc = math.copysign(1, j1 - j2)
        new_i = i2 + iinc
        new_j = j2 + jinc

        if new_i == i1 and new_j == j1:
            return True
        if point_point_dist(path1[new_i], path2[new_j] > GLUE_THRESH):
            return False
        
        i2, j2 = new_i, new_j

"""Exactly what it sounds like. Returns true if left has closer dist, else false"""
def first_intersection_better(path1, path2, intersection1, intersection2):
    i1p1, i1p2 = path1[intersection1[0]], path2[intersection1[1]]
    i2p1, i2p2 = path1[intersection2[0]], path2[intersection2[1]]
    i1_dist = point_point_dist(i1p1, i1p2)
    i2_dist = point_point_dist(i2p1, i2p2)
    return i1_dist < i2_dist

"""given a list of intersections, removes trivial ones (point intersecting self)"""
def remove_self_matches(intersections):
    i = 0
    while i < len(intersections):
        if intersections[i][0] == intersections[i][1]:
            intersections.pop(i)
        else:
            i += 1

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
        points = shuffle(points)
        for point in points:
            if len(neighbors := graph[point]) == 2:
                n1, n2 = neighbors
                if importance(point, n1, n2) < IMPORTANCE_THRESH:
                    points.remove(point)
                    graph[n1].remove(point)
                    graph[n1].append(n2)
                    graph[n2].remove(point)
                    graph[n2].append(n1)
                    del graph[point]
                    break
        else:
            done = True

"""
How important a point is to the structure of drawing graph
Precondition: point should always be a degree 2 vertex
"""
def importance(graph, point):
    lneighbor = graph[point][0]
    rneighbor = graph[point][1]

    ldist = point_point_dist(lneighbor, point)
    rdist = point_point_dist(rneighbor, point)
    angle = angle_measure(lneighbor, point, rneighbor)

    return angle ** ANGLE_WEIGHT * (ldist + rdist)

"""
calculates the measure of angle abc in radians
Adapted from an answer to this stack overflow post:
https://stackoverflow.com/questions/35176451/python-code-to-calculate-angle-between-three-point-using-their-3d-coordinates
"""
def angle_measure(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(b)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.arccos(cosine_angle)