import numpy as np
import math

from edges import closest_point

################ HYPERPARAMETERS ####################
XY_STEP = 0.00001
THETA_STEP = 0.0001
R_STEP = 0.001
GAMMA_STEP = 0.00001

REGULARIZATION_CONST = 0.1
LEARNING_RATE = 0.01


"""
Returns the loss of an embedding of points in the graph
Does so by finding the best subgraph corresponding to the embedding
and calculates the loss between the points and the subgraph
"""
def embedding_loss(points, graph, parameters):
    points = embed(points, parameters)
    subgraph = representative_subgraph()
    return regularized_loss(points, subgraph, parameters)

"""Finds subgraph minimizing regularized loss for a given embedding"""
def representative_subgraph(points, graph, parameters):
    img = image(points, graph)
    return prune(points, img, parameters)

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
def image(points, graph):
    edges = []
    for point in points:
        new_edge = closest_edge(point, graph)
        if new_edge not in edges:
            edges.append(new_edge)
    return edges

"""Finds the closest edge by euclidian distance to a point"""
def closest_edge(point, graph):
    closest_distance = math.inf
    for edge in graph:
        new_dist = point_to_line_segment_distance(point, edge)
        if new_dist < closest_distance:
            closest_distance = new_dist
            closest = edge
    return closest

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
def regularized_loss(points, edges, parameters):
    _, _, _, r, gamma = parameters
    
    points2edges = 0
    for point in points:
        points2edges += point_to_line_segment_distance(point, closest_edge(point, edges)) ** 2
    points2edges /= len(points)

    vertices2points = 0
    for edge in edges:
        v1, v2 = edge
        m = ((v1[0] + v2[0])/2 , (v1[1] + v2[1]))
        vertices2points = vertices2points \
                + closest_point(v1, points)[1] ** 2 \
                + closest_point(v2, points)[1] ** 2 \
                + closest_point(m, points)[1] ** 2
    vertices2points *= REGULARIZATION_CONST
    vertices2points /= 3 * len(edges)

    return (points2edges + vertices2points) / (r*r*gamma)


"""Prunes the subgraph to minimize regularized loss"""
def prune(points, edges, parameters):
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
        edges = edges.copy().remove(problem_edge)
        prune(points, edges, parameters)
    else:
        return edges
    
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

"""For testing"""
def main():
    tuple1 = (1, 2)
    tuple2 = (3, 4)
    sum = tuple1
    print(sum)

if __name__ == "__main__":
    main()