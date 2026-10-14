from cmath import inf, sqrt
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
    
    def intersects(self, x_c, y_c, radius):
        x_min = self.x_center - (self.width/2.0)
        x_max = self.x_center + (self.width/2.0)
        y_min = self.y_center - (self.height/2.0)
        y_max = self.y_center + (self.height/2.0)
        
        px = max(x_min, min(x_c, x_max))
        py = max(y_min, min(y_c, y_max))
        d2 = (x_c-px)**2 + (y_c-py)**2
        
        return d2 <= (radius**2)
    
    def distance(self, x_q, y_q):
        x_min = self.x_center - (self.width/2.0)
        x_max = self.x_center + (self.width/2.0)
        y_min = self.y_center - (self.height/2.0)
        y_max = self.y_center + (self.height/2.0)
        
        px = max(x_min, min(x_q, x_max))
        py = max(y_min, min(y_q, y_max))
        d2 = (x_q-px)**2 + (y_q-py)**2
        
        return sqrt(d2)
        

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
    
    def range_search(self, x_c: float, y_c: float, radius: float):
        results: List[Point] = []
        self._range_search(self.root, x_c, y_c, radius, results)
        return results
        
    def _range_search(self, node:Node, x_c, y_c, radius, results):
        if not(node.boundary.intersects(x_c, y_c, radius)):
            return
        if node.north_w is None:
            for p in node.points:
                d2 = (x_c-p.x)**2 + (y_c-p.y)**2
                if d2 <= radius**2:
                    results.append(p)
        else:
            self._range_search(node.north_w, x_c, y_c, radius, results)
            self._range_search(node.north_e, x_c, y_c, radius, results)
            self._range_search(node.south_w, x_c, y_c, radius, results)
            self._range_search(node.south_e, x_c, y_c, radius, results)
    
    def nearest_neighbor(self, x_query, y_query):
        campeon = [None, inf]
        self._nearest_neighbor(self.root, x_query, y_query, campeon)
        return campeon[0]

    def _nearest_neighbor(self, node: Node, x_query, y_query, campeon):
        d = node.boundary.distance(x_query, y_query)
        if d >= campeon[1]:
            return
        if node.north_w is None:
            for p in node.points:
                d = sqrt((x_query-p.x)**2 + (y_query - p.y)**2)
                if d < campeon[1]:
                    campeon[0] = p
                    campeon[1] = d
        else:
            hijos = [node.north_w, node.north_e, node.south_w, node.south_e]
            hijos.sort(key=lambda hijo: hijo.boundary.distance(x_query, y_query))
            
            for hijo in hijos:
                self._nearest_neighbor(hijo, x_query, y_query, campeon)
