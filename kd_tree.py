import numpy as np

"""A kd-tree used to find closest points. Written by chat-GPT"""
class KDTree:
    def __init__(self, points):
        self.tree = self.build_tree(points)
        
    class Node:
        def __init__(self, point, left, right):
            self.point = point
            self.left = left
            self.right = right
            
    
    def build_tree(self, points, depth=0):
        if len(points) == 0:
            return None
        
        k = points.shape[1]
        axis = depth % k
        
        sorted_points = points[points[:, axis].argsort()]
        mid = len(points) // 2
        
        return self.Node(sorted_points[mid], 
                          self.build_tree(sorted_points[:mid], depth + 1), 
                          self.build_tree(sorted_points[mid+1:], depth + 1))
        
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
            
            k = point.shape[0]
            axis = depth % k
            
            if point[axis] < node.point[axis]:
                search(node.left, depth + 1)
                if point[axis] + best_dist >= node.point[axis]:
                    search(node.right, depth + 1)
            else:
                search(node.right, depth + 1)
                if point[axis] - best_dist <= node.point[axis]:
                    search(node.left, depth + 1)
            
        search(self.tree)
        return best_point
