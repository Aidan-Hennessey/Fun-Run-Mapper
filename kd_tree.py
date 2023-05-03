import numpy as np

"""A kd-tree used to find closest points. Written (mostly) by chat-GPT"""
class KDTree:
    def __init__(self, points):
        if isinstance(points, list):
            points = np.array(points)
        self.tree = self.build_tree(points)
        
    class Node:
        def __init__(self, point, left, right):
            self.point = point
            self.left = left
            self.right = right
            
    
    def build_tree(self, points, depth=0):
        if len(points) == 0:
            return None
        
        axis = depth % 2
        
        sorted_points = points[points[:, axis].argsort()]
        mid = len(points) // 2
        
        return self.Node(sorted_points[mid], 
                          self.build_tree(sorted_points[:mid], depth + 1), 
                          self.build_tree(sorted_points[mid+1:], depth + 1))
        
    """returns the closest point in the tree to point in logarithmic time"""
    def closest_point(self, point):
        best_point = None
        best_dist = np.inf
        
        def search(node, depth=0):
            nonlocal best_point, best_dist
            
            if node is None:
                return
            
            dist = np.linalg.norm(point - node.point)
            
            if dist < best_dist:
                best_point = node.point
                best_dist = dist
            
            axis = depth % 2
            
            if point[axis] < node.point[axis]:
                search(node.left, depth + 1)
                if point[axis] + best_dist >= node.point[axis]:
                    search(node.right, depth + 1)
            else:
                search(node.right, depth + 1)
                if point[axis] - best_dist <= node.point[axis]:
                    search(node.left, depth + 1)
            
        search(self.tree)
        return tuple(best_point)
    
    """
    returns all points within radius of target. 
    Worst-case linear but should be prtty good on average
    It's also impossible to have an alg for this that has worst-case runtime
    better than linear anyway so I'm happy with this
    """
    def query_radius(self, target, radius):
        results = []
        self._query_radius(self.tree, target, radius, results)
        return results
    
    def _query_radius(self, node, target, radius, results, depth=0):
        if node is None:
            return
        
        if np.linalg.norm(node.point - target) <= radius:
            results.append(node.point)
        
        axis = depth % 2
        if target[axis] - radius < node.point[axis]:
            self._query_radius(node.left, target, radius, results, depth + 1)
        if target[axis] + radius > node.point[axis]:
            self._query_radius(node.right, target, radius, results, depth + 1)

    def add(self, point):
        def insert(node, point, depth):
            if node is None:
                return self.Node(point, None, None)

            axis = depth % 2

            if point[axis] < node.point[axis]:
                node.left = insert(node.left, point, depth + 1)
            else:
                node.right = insert(node.right, point, depth + 1)

            return node
        
        if not isinstance(point, np.ndarray):
            point = np.array(point)
            
        self.tree = insert(self.tree, point, 0)

    def remove(self, point):
        if not isinstance(point, np.ndarray):
            point = np.array(point)

        self.tree = self._remove(self.tree, point)
        
    def _remove(self, node, point):        
        if node is None:
            return None
        elif np.array_equal(node.point, point):
            if node.right:
                right_min = self._min(node.right, 0)
                node.point = right_min
                node.right = self._remove(node.right, right_min)
                return node
            else:
                return node.left
        elif point[node.depth % 2] < node.point[node.depth % 2]:
            node.left = self._remove(node.left, point)
            return node
        else:
            node.right = self._remove(node.right, point)
            return node
        
    def _min(self, node, depth):
        if node is None:
            return None
        elif node.left is None:
            return node.point
        else:
            return self._min(node.left, depth + 1)
        
    def pop_closest(self, point):
        closest = self.closest_point(point)
        self.remove(closest)
        return tuple(closest)