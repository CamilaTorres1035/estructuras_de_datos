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