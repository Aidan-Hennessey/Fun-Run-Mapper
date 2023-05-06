import numpy as np

from fast_gradient_decent import edges_as_points, point_point_dist
from kd_tree import KDTree

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
            edges.append(self.path[i], self.path[i+1])
        return edges

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
                return None
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