import numpy as np
import heapq
import math

from .fast_gradient_decent import edges_as_points, point_point_dist
from .kd_tree import KDTree

STABILITY = 4 # controls how stringently the walk tries to stick to the path

"""
A segment is a path in the drawing connecting two critical points.
Our algorithm works by identifying critical points, embedding them,
and then drawing the segments between them on the map.
Note: segments are immutable (or should at least be treated as such)
"""
class Segment:
    def __init__(self, path) -> None:
        self.path = path
        self.size = point_point_dist(path[0], path[-1])
        self.edges = self.__edges_from_path()
        self.points2edges = {}
        self.kdtree = KDTree(edges_as_points(self.edges, self.points2edges))

    """Fills in the edge list according to the path"""
    def __edges_from_path(self):
        edges = []
        for i in range(len(self.path) - 1):
            edges.append((self.path[i], self.path[i+1]))
        return edges
    
    """a to-string for segment"""
    def print(self):
        print(self.path)

    """
    Returns a list of edges in the graph which form a path from start to end 
    and which resembles the segement in shape
    """
    def draw(self, graph) -> list:
        path = []
        used = set()
        current = self.path[0]
        used.add(current)
        while current != self.path[-1]:
            if (next := self.__continue_path(current, graph, used)) is not None:
                path.append((current, next))
                used.add(next)
                current = next
            else:
                print("No path found; finishing with A*")
                points = [edge[0] for edge in path] # first point in each edge
                points.append(path[-1][1]) # include very last point
                return self.__finish(points, graph)
        print("path found :)")
        return path
                
    """returns the best next step in the drawing, or None if we should give up"""
    def __continue_path(self, current, graph, used):
        candidates = graph[current]
        candidates = filter(lambda x: x not in used, candidates)
        best_candidate = None
        greatest_alignment = 0
        for cand in candidates:
            if (cand_alignment := self.__alignment(current, cand)) > greatest_alignment:
                best_candidate = cand
                greatest_alignment = cand_alignment
        return best_candidate
    
    """Determines how good a next step candidate is"""
    def __alignment(self, current, candidate):
        goal_vec = self.__get_vec(current)
        cand_vec = (np.array(candidate) - np.array(current)) / point_point_dist(current, candidate)
        return np.dot(goal_vec, cand_vec)

    """queries the segment's vector field at point"""
    def __get_vec(self, point):
        nearest_point = self.kdtree.closest_point(point)
        correction_vec = (np.array(nearest_point) - np.array(point)) / self.size

        nearest_edge = self.points2edges[nearest_point]
        edge_start, edge_end = np.array(nearest_edge[1]), np.array(nearest_edge[0])
        progress_vec = (edge_end - edge_start) / point_point_dist(edge_start, edge_end)

        return STABILITY * correction_vec + progress_vec
    
    """Takes a partially-drawn path and finishes it with A*"""
    def __finish(self, path, graph) -> list:
        # find the closest point in path to end
        end = self.path[-1]
        closest_dist = math.inf
        for i, point in enumerate(path):
            if (new_dist := point_point_dist(point, end)) < closest_dist:
                closest_dist = new_dist
                closest_index = i
        
        # do A* from closest point to end
        return path[:closest_index] + self.a_star(graph, start=path[closest_index])

    """
    Computes a path connecting this segment's endpoints without regard for the 
    shape of the segment. In particular, implements A* algorithm. Written by chat-GPT.

    Params: graph is the graph of college hill in dict of neighbors form
    Returns: a list of edges giving a directish path between the segment endpoints
    """
    def a_star(self, graph, start=None):
        if start == None:
            start = self.path[0]
        end = self.path[-1]
        # Open set to keep track of nodes to be explored
        open_set = []
        # Set to store visited nodes
        closed_set = set()
        # Dictionary to store the node the current node came from
        came_from = {}
        # Dictionary to store the cost of reaching a node from the start node
        g_score = {start: 0}
        # Dictionary to store the estimated total cost of reaching the end node from the start node
        f_score = {start: point_point_dist(start, end)}

        # Push the start node into the open set with its estimated total cost
        heapq.heappush(open_set, (f_score[start], start))

        while open_set:
            # Pop the node with the lowest total cost from the open set
            current = heapq.heappop(open_set)[1]

            # Check if the current node is the end node
            if current == end:
                # Path found, reconstruct and return the path
                return self.__reconstruct_path(came_from, current)

            # Add the current node to the closed set
            closed_set.add(current)

            # Explore the neighbors of the current node
            for neighbor in graph[current]:
                # The cost for each edge is assumed to be 1
                tentative_g_score = g_score[current] + 1

                if neighbor in closed_set and tentative_g_score >= g_score.get(neighbor, float('inf')):
                    # Ignore this neighbor if it has already been visited and a better path has been found
                    continue

                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    # Update the best path to reach the neighbor
                    came_from[neighbor] = current
                    # Update the cost to reach the neighbor from the start node
                    g_score[neighbor] = tentative_g_score
                    # Update the estimated total cost of reaching the end node from the start node
                    f_score[neighbor] = tentative_g_score + point_point_dist(neighbor, end)
                    if neighbor not in closed_set:
                        # Add the neighbor to the open set if it hasn't been visited yet
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # No path found
        return None

    """Reconstructs the path from the start node to the current node"""
    def __reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        return path[::-1]
    
    """
    the loss of a path through the graph with respect to this segment
    In the distant future we would learn this from user input
    For now it will be a combination of location and direction error
    """
    def loss(self, path):
        points, points_to_edges = self.__sample_points(path)

        sum_of_squared_errors = 0
        for point in points:
            dist_err = point_point_dist(self.kdtree.closest_point(point), point)
            angle_err = self.__angle_err(point, points_to_edges(point))
            sum_of_squared_errors += (dist_err * angle_err) ** 2

        return sum_of_squared_errors

    """
    Samples points from consumed path to be evaluated for loss. Written by chat-GPT.
    
    Params:
        path - the path to sample from, as a list of points
        num_points - the number of points to sample. Defaults to 50
    Returns:
        sampled_points - a list of points that we sampled
        points_to_edges_dict - a dictionary from the elements of sampled points to the
                            edges on which they live
    """
    def __sample_points(self, path, num_points=50):
        total_length = 0.0
        lengths = []

        # Calculate the total length of the path and the lengths between consecutive vertices
        for i in range(len(path) - 1):
            length = point_point_dist(path[i], path[i+1])
            total_length += length
            lengths.append(length)

        # Calculate the distance between each sample point
        distance_between_points = total_length / (num_points - 1)

        sampled_points = []
        current_distance = 0.0
        points_to_edges_dict = {}

        # Sample the points along the path
        for i in range(len(lengths)):
            length = lengths[i]
            while current_distance <= length and len(sampled_points) < num_points:
                ratio = current_distance / length
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                x = x1 + (x2 - x1) * ratio
                y = y1 + (y2 - y1) * ratio
                sampled_points.append((x, y))
                points_to_edges_dict[(x, y)] = (path[i], path[i+1])
                current_distance += distance_between_points

            current_distance -= length

        return sampled_points, points_to_edges_dict
    
    """how far off a point is from the user-drawn curve"""
    def __angle_err(self, point, edge):
        nearest_edge = self.points2edges[self.kdtree.closest_point(point)]

        a, b = np.array(edge[0]), np.array(edge[1])
        c, d = np.array(nearest_edge[0]), np.array(nearest_edge[1])
        point_vec = a - b
        nearest_edge_vec = c - d

        return misalignment(point_vec, nearest_edge_vec)
    
"""Angle between vectors"""
def misalignment(v1 : np.ndarray, v2 : np.ndarray):
    cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return np.arccos(cosine_angle)

def main():
    seg = Segment([(7, 7)])
    sampling = seg.sample_points([(0, 0), (0, 10), (12, 15), (0, 24), (11, 24)])
    print(sampling)
    
if __name__ == "__main__":
    main()
