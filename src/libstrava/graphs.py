"""
Hirearchy:
subgraph - generates subgraph from drawing
    glue - glues paths together
        find_intersections - finds pairs which are intended to intersect
            local_min_match - GDs to locally closest pair
            remove_clones - removes a single clone, as defined below
                clones - whether 2 intersections can be turned into eachother continously
                first_intersection_better - pair of "intersecting" points are closer than other
        remove_self_matches - remove intersections of point with self
        do_the_glue - edits graph dict to incorporate found intersections
        shave_stubble - removes short hairs sticking out
            hair_length - computes length of hair
            remove_hair - removes hair from graph
    segmentize - breaks graph up into distinct segments
        compress - removes "unimportant" vertices to speed up segmentation
            importance - measured using angle at vertex + distance to neighbors
                angle_measure - calculates angle at a degree 2 vertex
        get_embedding - randomly embeds drawing in map
            get_embedding_params - create random parameter bundle
        recover_params - calc parameter bundle corresponding to pair of embedded points
        Segment - 
            edges_from_path
    draw - each segment draws itself a path
        __continue_path - finds best next intersection to move to
            __alignment - alignment of possible continuation w/ vector field
                __get_vec - samples vector field w/ which we want to be aligned
        __finish - finihses attempted draw with A*
            a_star - connects points in graph
                __reconstruct_path

NOTE ON GRAPH REPRESENTATION:
In most cases, graphs are represented as dictionaries mapping from vertices to 
neighboring vertices. Exceptions include the input to glue, which is a list
of lists of points, with the understanding that each list corresponds to a 
path in the natural way (neighboring points in a list are adjacent in graph).
"""
import math
import numpy as np
import random
from functools import reduce

from kd_tree import KDTree
from fast_gradient_decent import point_point_dist, embed
from segment import Segment
from edges import read_edges
from points import read_gps

root = "../.."

GLUE_THRESH = 0.02
STUBBLE_THRESH = 0.04
IMPORTANCE_THRESH = 0.001
ANGLE_WEIGHT = 2
COMPRESS = False

############################## GLUE SHIT ###################################

"""glues paths together into a graph by connecting ends to things if close"""
def glue(paths):
    glued_graph = {}

    kdtrees = list(map(lambda x: KDTree(x), paths))
    points_to_indices = []
    for path in paths:
        path_dict = {}
        points_to_indices.append(path_dict)
        for i, point in enumerate(path):
            path_dict[point] = i

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
            connections = find_intersections(paths[i], paths[j], kdtrees[j], points_to_indices[j])
            if i == j:
                # removes (i, i) and one of (i, j) and (j, i)
                connections = remove_self_matches(connections)

            for con_i, con_j in connections:
                do_the_glue(glued_graph, paths[i], paths[j], con_i, con_j)
    
    return glued_graph

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
def find_intersections(path1, path2, path2KDtree : KDTree, point2index : dict):
    intersections = []

    # add every pair within thresh
    for i, p1 in enumerate(path1):
        matches = path2KDtree.query_radius(p1, GLUE_THRESH)
        for match in matches:
            intersections.append((i, j := point2index[tuple(match)]))
    
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
def clones(path1, path2, intersection1 : tuple[int, int], intersection2 : tuple[int, int]):
    i1, j1 = intersection1
    i2, j2 = intersection2

    assert(i1 >= 0 and i1 < len(path1))
    assert(i2 >= 0 and i2 < len(path1))
    assert(j1 >= 0 and j1 < len(path2))
    assert(j2 >= 0 and j2 < len(path2))

    while True:
        if i2 > i1:
            iinc = -1
        elif i2 == i1:
            iinc = 0
        else:
            iinc = 1

        if j2 > j1:
            jinc = -1
        elif j2 == j1:
            jinc = 0
        else:
            jinc = 1

        new_i = i2 + iinc
        new_j = j2 + jinc

        if new_i == i1 and new_j == j1:
            return True
        if point_point_dist(path1[new_i], path2[new_j]) > GLUE_THRESH:
            return False
        
        i2, j2 = new_i, new_j

"""Exactly what it sounds like. Returns true if left has closer dist, else false"""
def first_intersection_better(path1, path2, intersection1, intersection2):
    i1p1, i1p2 = path1[intersection1[0]], path2[intersection1[1]]
    i2p1, i2p2 = path1[intersection2[0]], path2[intersection2[1]]
    i1_dist = point_point_dist(i1p1, i1p2)
    i2_dist = point_point_dist(i2p1, i2p2)
    return i1_dist < i2_dist

"""given a list of intersections, removes trivial ones and repeats"""
def remove_self_matches(intersections):
    i = 0
    while i < len(intersections):
        if intersections[i][0] == intersections[i][1]:
            intersections.pop(i)
        else:
            i += 1

    return list(set(sorted(intersections)))

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
def remove_hair(tip : tuple[float], graph : dict[tuple[float], list[tuple[float]]]) -> None:
    cur_point = tip

    while len(graph[cur_point]) == 1:
        next_point = graph[cur_point][0]
        
        graph[next_point].remove(cur_point)
        del graph[cur_point]

        # update location
        cur_point = next_point

########################### END GLUE SHIT ###################################
############################ SEGMENTIZE #####################################

"""
We have a glued graph. We need to split it into segments so that we can draw each segment.
This function handles that.
"""
def segmentize(glued_graph, ch_points_tree : KDTree) -> list[Segment]:
    if COMPRESS:
        compress(glued_graph)

    segments = []

    critical_vertices = set()
    for vertex in glued_graph.keys():
        if len(glued_graph[vertex]) != 2:
            critical_vertices.add(vertex)
    critical_vertices = list(critical_vertices)

    embeddings = {k : v for (k, v) in zip(critical_vertices, get_embedding(ch_points_tree, list(critical_vertices)), strict=True)}
    
    for vertex in critical_vertices:
        for neighbor in glued_graph[vertex]:
            # follow this path
            last = vertex
            current = neighbor
            path = [last, current]
            while len(neighbors := glued_graph[current]) == 2:
                if neighbors[0] == last:
                    next = neighbors[1]
                else:
                    next = neighbors[0]
                path.append(next)
                last = current
                current = next

            # (vertex, current) are endpoints
            embedded_endpoints = (embeddings[vertex], embeddings[current])
            params = recover_parameters((vertex, current), embedded_endpoints)

            path = embed(path, params)

            # ensure endpoints exactly match graph intersections
            path[0] = embeddings[vertex]
            path[-1] = embeddings[current]

            if current == vertex: # we just traversed a loop
                # split loop into 2 segments
                path_len = len(path)
                
                # ensure endpoints of split segments are intersections on graph
                break_point = path[path_len // 2]
                break_point = ch_points_tree.closest_point(break_point)
                path[path_len // 2] = break_point

                segments.append(Segment(path[: path_len // 2 + 1]))
                segments.append(Segment(path[path_len // 2 :]))

            # so as to avoid double-counting segments
            # we'll miss a segment if both its endpoints get hashed to the same thing, but nbd
            if hash(tuple(vertex)) < hash(tuple(current)):
                segments.append(Segment(path))

    return segments

"""Compresses the drawing representation to one without many edges"""
def compress(graph):
    points = graph.keys()
    done = False
    while not done:
        points = random.shuffle(points)
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

    if lneighbor == rneighbor:
        return math.inf

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

"""
Gets a representation of the vertices of the fundemental graph in vertices of the college hill graph

Params:
    ch_points_tree - a kd tree made from the college hill graph vertices (combined.txt)
    fg_points - the vertices of the fundemental graph
"""
def get_embedding(ch_points_tree : KDTree, fg_points):
    embedded_points = embed(fg_points, get_embedding_params())
    # map points into college hill points
    map_image = map(lambda x: ch_points_tree.closest_point(x), embedded_points)
    # add back points that we removed
    # map(lambda x: ch_points_tree.add(x), injection_image) <- used when injecting

    return list(map_image)

def get_embedding_params():
    x = 41.823 #+ 0.017 * np.random.rand()
    y = -71.388 #- 0.015 * np.random.rand()
    theta = 0#2 * math.pi * np.random.rand()
    r = 0.005 #+ 0.01 * np.random.rand()
    gamma = 1#0.8 + 0.4 * np.random.rand()
    return x, y, theta, r, gamma

"""
Given an input edge and output edge, determines the unique gamma=1 bundle
which could have produced the transformation. Written by chat-GPT.

Params:
    input - 2 input points
    output - the embeddings of the 2 points
Returns:
    a full parameter bundle: x, y, theta, r, gamma, with gamma guaranteed to be 1
"""
def recover_parameters(input, output):
    input1, input2 = input
    output1, output2 = output

    # Compute the angle of rotation theta
    delta_x = input2[0] - input1[0]
    delta_y = input2[1] - input1[1]
    theta = math.atan2(delta_y, delta_x) - math.atan2(output2[1] - output1[1], output2[0] - output1[0])

    # Compute the scaling factor r
    distance_input = math.sqrt(delta_x ** 2 + delta_y ** 2)
    distance_output = math.sqrt((output2[0] - output1[0]) ** 2 + (output2[1] - output1[1]) ** 2)
    r = distance_output / distance_input

    # Compute the translation x and y
    x = output1[0] - r * (input1[0] * math.cos(theta) - input1[1] * math.sin(theta))
    y = output1[1] - r * (input1[0] * math.sin(theta) + input1[1] * math.cos(theta))

    return x, y, theta, r, 1

############################ END SEGMENTIZE #############################
########################### GRAPH FROM EDGES ############################

"""given a list of edges, constructs a dictionary graph"""
def graph_from_edges(edges):
    graph = {}
    for edge in edges:
        p1, p2 = edge
        if p1 not in graph:
            graph[p1] = []
        if p2 not in graph:
            graph[p2] = []

        graph[p1].append(p2)
        graph[p2].append(p1)

    return graph

"""
The big guy. Takes in a drawing, represented as a list of paths, and outputs
an exstravaganza run as a list of edges.
"""
def get_subgraph(ch_graph, ch_points_tree, paths):
    glued_graph = glue(paths)
    print(glued_graph)
    segments = segmentize(glued_graph, ch_points_tree)
    print([segment.print() for segment in segments])
    drawn_segments = list(map(lambda x: x.draw(ch_graph), segments))
    return reduce(lambda x, y: x + y, drawn_segments, [])

def main():
    graph = graph_from_edges(read_edges(f"{root}/data/edge_list.txt"))
    points_tree = KDTree(list(graph.keys()))
    drawing = [[(0.5, 0.5), (0.7, 0.7), (0.9, 0.9)], \
               [(0.1, 0.1), (0.1, 0.5), (0.51, 0.51), (0.5, 0.1), (0.11, 0.11)]]
    
    subgraph = get_subgraph(graph, points_tree, drawing)
    print(subgraph)

if __name__ == "__main__":
    main()  

########################### STUPID USELESS GARBAGE ######################################

"""
NOTE: BAD! We should not actually use this. Leaving here only bc I might want to reuse pieces

Returns a fully condenced version of the graph (very few degree 2 vertices)
There's a lot of stuff going on here. Loops are represented, probably poorly
"""
def fundemental_graph(graph):
    graph = graph.copy()
    while not done:
        points = graph.keys()
        points = random.shuffle(points)
        for point in points:
            if len(neighbors := graph[point]) == 2:
                n1, n2 = neighbors
                if n1 != n2: # this is so that FG has loops working
                    points.remove(point)
                    graph[n1].remove(point)
                    graph[n1].append(n2)
                    graph[n2].remove(point)
                    graph[n2].append(n1)
                    del graph[point]
                    break
        else:
            done = True

    return graph

"""
Random walk from start with a bias in end's direction. 
Terminates upon reaching end or when no new points can be visited.
Returns none in the latter case

TODO: add momentum - momentum can be initialized based on direction 
out in compressed graph. Momentum will make the graph way more human

Params:
    graph - graph of college hill
    start - start point of the random walk
    end - end point of the random walk
Returns:
    A list of edges detailing the walk in order from start to end
    None if we get stuck before completing such a walk
    NOTE: edges are from earlier point to later point, NOT sorted lexicographically.
    They will need to be passed through sorted() before compared for equality with 
    edges in the college hill edge list
"""
def semi_random_walk(graph, start, end):
    walk = []
    visited = [start]
    current_point = start
    while current_point != end:
        targets = graph[current_point]
        targets = [point for point in targets if point not in visited] # by chat-GPT
        if len(targets) == 0:
            return None
        next_point = softmax_choose(targets, current_point)
        walk.append((current_point, next_point))
        current_point = next_point
    return walk

"""non-deterministically chooses a next point in the biased random walk. Written by chat-GPT"""
def softmax_choose(points, target):
    points = np.array(points)
    target = np.array(target)
    distances = np.linalg.norm(points - target, axis=1)
    normalized_distances = (distances - np.min(distances)) / (np.max(distances) - np.min(distances)) + 0.1
    # ^^ 0.1 is a parameter controlling how much the random walk wanders
    softmax_vals = np.exp(normalized_distances) / np.sum(np.exp(normalized_distances))
    return tuple(points[np.random.choice(len(points), p=softmax_vals)])