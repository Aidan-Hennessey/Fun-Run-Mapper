import math
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import cv2

from points import read_gps, plot_point, gps2pixel

"""GLOBALS"""
corners1 = ((41.837521, -71.413896), (41.817705, -71.371781))
fname1 = "./ss 1.png"

corners2 = ((41.848696763227515, -71.41241538461539), (41.8333626547619, -71.37795461538461))
fname2 = "./ss 2.png"

corners = corners2
fname = fname2
"""END GLOBALS"""

"""
Not actually the euclidian distance, but an easy to compute metric that corresponds pretty well
Precisely, it is the reciprocal eccentrcity of the ellipse with foci at the endpoints of the edge
which contains point
"""
def point_edge_dist(point, edge):
    p1, p2 = edge
    focal_length = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) + 0.0000001
    major_axis_length = \
            math.sqrt((p1[0] - point[0])**2 + (p1[1] - point[1])**2) \
            + math.sqrt((point[0] - p2[0])**2 + (point[1] - p2[1])**2)
    return major_axis_length / focal_length

"""
Returns whether end is to the [direction] of start

Params:
    start - 2tuple of floats
    end - 2tuple of floats
    direction - a string - one of north, south, east, and west
Returns:
    a bool - whether end is in that direction from start
"""
def is_in_direction(start, end, direction) -> bool:
    x_displacement = end[0] - start[0]
    y_displacement = end[1] - start[1]
    if direction == "north":
        return (y_displacement > 0) and (abs(y_displacement) - abs(x_displacement) >= 0)
    elif direction == "south":
        return (y_displacement < 0) and (abs(y_displacement) - abs(x_displacement) >= 0)
    elif direction == "east":
        return (x_displacement > 0) and (abs(x_displacement) - abs(y_displacement) > 0)
    elif direction == "west":
        return (x_displacement < 0) and (abs(x_displacement) - abs(y_displacement) > 0)
    else:
        print("is_in_direction got invalid direction")
        return False

"""
Finds the closest point in a cardinal direction to target

Params:
    target - a 2tuple - the point to find a neighbor for
    points - (n, 2) array - the points to search through
    direction - the direction in which to look
Returns:
    a 2tuple - the coordinates of the closest point in the desired direction
"""
def find_closest_in_direction(target, points, direction):
    closest = None
    closest_distance = math.inf
    for point in points:
        if is_in_direction(target, point, direction):  
            distance = math.sqrt((point[0] - target[0])**2 + (point[1] - target[1])**2)
            if distance < closest_distance:
                closest = point
                closest_distance = distance
    return closest

"""
Adds an edge to from each point to its closest neighbor in each direction
Edges are represented as (point, point) with the points sorted lexicographically
"""
def griddy_edges(points):
    edges = []
    for point in points:
        for dir in ["north", "south", "east", "west"]:
            closest = find_closest_in_direction(point, points, dir)
            if closest is not None:
                edges.append(tuple(sorted((point, closest))))
    return edges

def plot_edge(img, edge, imageconf):
    (x1, y1), (x2, y2) = edge
    p1 = gps2pixel((x1, y1), corners, imageconf)
    p2 = gps2pixel((x2, y2), corners, imageconf)
    (x1, y1), (x2, y2) = p1, p2

    p1_inbounds = (x1 >= 0 and x1 < imageconf[0] and y1 >= 0 and y1 < imageconf[1])
    p2_inbounds = (x2 >= 0 and x2 < imageconf[0] and y2 >= 0 and y2 < imageconf[1])

    if p1_inbounds and p2_inbounds:
        img = cv2.line(img, p1, p2, (0, 255, 0), thickness=1)

    return img

"""
A graphical interface to make an edge list for our graph
"""
def main():
    # read in points
    points = read_gps("combined.txt")
    
    # make edge list with nearest neighbors
    edges = griddy_edges(points)

    # plot edges
    with Image.open(fname) as im:
        im = np.asarray(im)[:, :, :3]
        imageconf = im.shape[1], im.shape[0]

    for pt in points:
        px, py = gps2pixel(pt, corners, imageconf)
        im = plot_point(im, px, py, imageconf)
    for edge in edges:
        im = plot_edge(im, edge, imageconf)

    fig, ax = plt.subplots()
    ax.imshow(im)

    def onclick(event):
        point = int(event.xdata), int(event.ydata)
        closest = None
        closest_distance = math.inf
        for edge in edges:
            converted_edge = (gps2pixel(edge[0], corners, imageconf), gps2pixel(edge[1], corners, imageconf))
            distance = point_edge_dist(point, converted_edge)
            if distance < closest_distance:
                closest_distance = distance
                closest = edge
        print((gps2pixel(closest[0], corners, imageconf), gps2pixel(closest[1], corners, imageconf)))

    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    plt.title(fname)
    plt.show()

    # TODO: Interface to edit edge list

if __name__ == "__main__":
    main()