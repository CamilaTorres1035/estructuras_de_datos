from typing import List, Optional


class Point:
    def __init__(self, x:float, y:float) -> None:
        self.x = x
        self.y = y

class BoundingBox:
    def __init__(self, x_center: float, y_center: float, width: float, height: float) -> None:
        self.x_center = x_center
        self.y_center = y_center
        self.width = width
        self.height = height
    
    def contains_point(self, point: Point) -> bool:
        """Determina si un punto está dentro de los límites del rectángulo"""
        x_min = self.x_center - (self.width/2.0)
        x_max = self.x_center + (self.width/2.0)
        y_min = self.y_center - (self.height/2.0)
        y_max = self.y_center + (self.height/2.0)
        
        return (x_min <= point.x <= x_max and y_min<= point.y <= y_max)

class Node:
    def __init__(self, boundary: BoundingBox, capacity: int) -> None:
        self.boundary = boundary
        self.capacity = capacity
        self.points: List[Point] = []
        self.north_w: Optional['Node'] = None
        self.north_e: Optional['Node'] = None
        self.south_w: Optional['Node'] = None
        self.south_e: Optional['Node'] = None
    
class QuadTree:
    def __init__(self, boundary: BoundingBox, capacity: int = 4) -> None:
        self.root = Node(boundary, capacity)
    
    def insertar(self, point: Point) -> bool:
        pass