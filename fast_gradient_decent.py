import numpy as np
import math

from edges import read_edges
from kd_tree import KDTree

################ HYPERPARAMETERS ####################
XY_STEP = 0.00001
THETA_STEP = 0.0001
R_STEP = 0.000001
GAMMA_STEP = 0.000001

REGULARIZATION_CONST = 0.2
LEARNING_RATE = 0.1
HOARDING_FACTOR = 3 # the higher this hyperparam, the less aggressively we'll prune

"""Return a better parameter bundle """
def gradient_decend(points, graph, parameters):
    x, y, theta, r, gamma = parameters
    xgrad, ygrad, theta_grad, rgrad, gamma_grad = gradient(points, graph, parameters)

    xgrad *= LEARNING_RATE
    ygrad *= LEARNING_RATE
    theta_grad *= LEARNING_RATE
    rgrad *= LEARNING_RATE
    gamma_grad *= LEARNING_RATE
    
    return x - xgrad, y - ygrad, theta - theta_grad, r - rgrad, gamma - gamma_grad

"""Compute the gradient using finite differences"""
def gradient(points, graph, parameters):
    x, y, theta, r, gamma = parameters
    unperturbed_loss = embedding_loss(points, graph, parameters)

    x_perturbed = (x + XY_STEP, y, theta, r, gamma)
    xgrad = (embedding_loss(points, graph, x_perturbed) - unperturbed_loss) / XY_STEP
    y_perturbed = (x, y + XY_STEP, theta, r, gamma)
    ygrad = (embedding_loss(points, graph, y_perturbed) - unperturbed_loss) / XY_STEP
    theta_perturbed = (x, y, theta + THETA_STEP, r, gamma)
    theta_grad = (embedding_loss(points, graph, theta_perturbed) - unperturbed_loss) / THETA_STEP
    r_perturbed = (x, y, theta, r + R_STEP, gamma)
    rgrad = (embedding_loss(points, graph, r_perturbed) - unperturbed_loss) / R_STEP
    gamma_perturbed = (x, y, theta, r, gamma + GAMMA_STEP)
    gamma_grad = (embedding_loss(points, graph, gamma_perturbed) - unperturbed_loss) / GAMMA_STEP

    return xgrad, ygrad, theta_grad, rgrad, gamma_grad

"""
Returns the loss of an embedding of points in the graph
Does so by finding the best subgraph corresponding to the embedding
and calculates the loss between the points and the subgraph
"""
def embedding_loss(points, graph, parameters):
    points = embed(points, parameters)

    #setup for image and fast_prune
    points_tree = KDTree(points)
    samples_to_parents = {}
    graph_points = edges_as_points(graph, samples_to_parents)
    graph_tree = KDTree(graph_points)

    img = image(points, graph_tree, samples_to_parents)

    image_tree = KDTree(edges_as_points(img, samples_to_parents))
    subgraph = fast_prune(points, points_tree, img, image_tree, samples_to_parents)

    subgraph_tree = KDTree(edges_as_points(subgraph, samples_to_parents))
    return regularized_loss(points, subgraph_tree, samples_to_parents)
    

"""Using a set of points in box-space and a parameter bundle, embeds the points in GPS coords"""
def embed(points, parameters):
    x, y, theta, r, gamma = parameters
    embedded_points = []
    for point in points:
        a, b = point
        embedding = (x + a*r*math.sin(theta) + b*gamma*r*math.cos(theta), y - a*r*math.cos(theta) + b*gamma*r*math.sin(theta))
        embedded_points.append(embedding)
    return embedded_points

"""Returns the image of the map from points to their closest edges"""
def image(points, graph_tree, samples_to_edges):
    edges = set()
    for point in points:
        new_edge = samples_to_edges[graph_tree.closest_point(point)]
        edges.add(new_edge)
    return list(edges)

"""Prunes the subgraph in a quick, heuristic way"""
def fast_prune(points, points_tree, edges, edges_tree, samples_to_parents):
    # calc average distance from points to edges
    points2edges_dist = 0
    for point in points:
        points2edges_dist += point_to_line_segment_distance(point, samples_to_parents[edges_tree.closest_point(point)])
    points2edges_dist /= len(points)
    # multiply by constant to get threshold
    threshold = HOARDING_FACTOR * points2edges_dist

    # remove bad edges (a bad edge is one that doesn't stay close to the points)
    for edge in edges:
        v1, v2 = edge
        m = (v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2
        v1_neighbor = points_tree.closest_point(v1)
        v2_neighbor = points_tree.closest_point(v2)
        m_neighbor = points_tree.closest_point(m)
        edge_badness = np.max([point_point_dist(v1, v1_neighbor), \
                            point_point_dist(v2, v2_neighbor), \
                            point_point_dist(m, m_neighbor)])
        if edge_badness > threshold and len(edges) > 1:
            edges.remove(edge)
    
    return edges

"""The euclidian distance between a point and an edge. Written by chat GPT"""
def point_to_line_segment_distance(point, edge):
    p = point
    e1, e2 = edge

    # Calculate the vector between e1 and e2
    e_vec = (e2[0] - e1[0], e2[1] - e1[1])

    # Calculate the vector between e1 and p
    p_vec = (p[0] - e1[0], p[1] - e1[1])

    # Calculate the dot product of e_vec and p_vec
    dot_product = e_vec[0] * p_vec[0] + e_vec[1] * p_vec[1]

    # Calculate the squared length of e_vec
    e_vec_squared_length = e_vec[0] ** 2 + e_vec[1] ** 2

    # Calculate the parameter along the line segment where the closest point to p lies
    if e_vec_squared_length == 0:
        print(edge)
    param = dot_product / e_vec_squared_length

    if param < 0:
        # The closest point to p is e1
        closest_point = e1
    elif param > 1:
        # The closest point to p is e2
        closest_point = e2
    else:
        # The closest point to p lies along the line segment
        closest_point = (e1[0] + param * e_vec[0], e1[1] + param * e_vec[1])

    # Calculate the distance between p and the closest point
    distance = math.sqrt((p[0] - closest_point[0]) ** 2 + (p[1] - closest_point[1]) ** 2)

    return distance

"""
Calculate the regularized loss of a subgraph and an emedding of points
MSE of points into edges + k * MSE of vertices into points
"""
def regularized_loss(points, edges_tree, samples_to_parents):
    points2edges = 0
    for point in points:
        points2edges += point_to_line_segment_distance(point, samples_to_parents[edges_tree.closest_point(point)]) ** 2
    points2edges /= len(points)

    return points2edges


"""Prunes the subgraph to minimize regularized loss"""
def prune(points, edges, parameters):
    if len(edges) <= 1:
        return edges

    best_loss = regularized_loss(points, edges, parameters)
    problem_edge = None
    for edge in edges:
        subgraph = edges.copy()
        subgraph.remove(edge)
        subgraph_loss = regularized_loss(points, subgraph, parameters)
        if subgraph_loss < best_loss:
            best_loss = subgraph_loss
            problem_edge = edge
    if problem_edge is not None:
        edges = edges.copy()
        edges.remove(problem_edge)
        return prune(points, edges, parameters)
    else:
        return edges
    
def point_point_dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

"""Returns a random intial parameter bundle"""
def random_init():
    x = 41.816 + 0.03 * np.random.rand()
    y = -71.380 - 0.028 * np.random.rand()
    theta = 2 * math.pi * np.random.rand()
    r = 0.008 + 0.008 * np.random.rand()
    gamma = 0.7 + 0.6 * np.random.rand()
    return x, y, theta, r, gamma

"""Takes a list of edges and discretizes it into a large list of points"""
def edges_as_points(edges, dict, fineness=10):
    points = []
    for edge in edges:
        points += edge_to_points(edge, dict, fineness)
    return points

def edge_to_points(edge, dict, fineness):
    (x1, y1), (x2, y2) = edge
    points = []
    for i in range(fineness + 1):
        x = x1 + (x2 - x1) * (i / fineness)
        y = y1 + (y2 - y1) * (i / fineness)
        points.append((x, y))
        dict[(x, y)] = edge
    return points

"""For testing"""
def main():
    points = []
    for _ in range(1000):
        points.append((np.random.rand(), np.random.rand()))
    edges = read_edges("edge_list.txt")
    parameters = random_init()

    print(parameters)
    print(embedding_loss(points, edges, parameters))
    for _ in range(10):
        parameters = gradient_decend(points, edges, parameters)
        print(parameters)
        print(embedding_loss(points, edges, parameters))

if __name__ == "__main__":
    main()