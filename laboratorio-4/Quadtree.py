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
    
    def insertar(self, point:Point) -> bool:
        # Rechazar directamente el punto si no pertenece a este cuadrante
        if not self.boundary.contains_point(point):
            return False
        
        # Aun hay espacio y el nodo NO se ha dividido
        if (len(self.points) < self.capacity and self.north_w is None):
            self.points.append(point)
            return True
        
        # El nodo está lleno, si  NO se ha dividido se divide
        if self.north_w is None:
            s_quad: List[BoundingBox] = self._dividir()
            self.north_w = Node(s_quad[0], self.capacity)
            self.north_e = Node(s_quad[1], self.capacity)
            self.south_w = Node(s_quad[2], self.capacity)
            self.south_e = Node(s_quad[3], self.capacity)
            for p in self.points:
                self._insertar_hijos(p)
            self.points = []
        
        # Propagamos al siguiente nivel
        return self._insertar_hijos(point)
    
    def _insertar_hijos(self, point:Point) -> bool:
        return (self.north_w.insertar(point) or 
                self.north_e.insertar(point) or 
                self.south_w.insertar(point) or 
                self.south_e.insertar(point))
    
    def _dividir(self):
        sub_cuadrantes = []
        sub_width = self.boundary.width/2.0
        sub_height = self.boundary.height/2.0
        x_center = self.boundary.x_center
        y_center = self.boundary.y_center
        sub_cuadrantes.append(BoundingBox(x_center-sub_width/2, y_center+sub_height/2, sub_width, sub_height))
        sub_cuadrantes.append(BoundingBox(x_center+sub_width/2, y_center+sub_height/2, sub_width, sub_height))
        sub_cuadrantes.append(BoundingBox(x_center-sub_width/2, y_center-sub_height/2, sub_width, sub_height))
        sub_cuadrantes.append(BoundingBox(x_center+sub_width/2, y_center-sub_height/2, sub_width, sub_height))
        return sub_cuadrantes
                
    
class QuadTree:
    def __init__(self, boundary: BoundingBox, capacity: int = 4) -> None:
        self.root = Node(boundary, capacity)
    
    def insertar(self, point: Point) -> bool:
        return self.root.insertar(point)