import math
from typing import List, Optional, Any, Tuple

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
    
    def intersects(self, x_c: float, y_c: float, radius: float) -> bool:
        """Verifica si el círculo de búsqueda intersecta la caja delimitadora (se utiliza en Range Search)"""
        hw = self.width / 2.0
        hh = self.height / 2.0
        x_min, x_max = self.x_center - hw, self.x_center + hw
        y_min, y_max = self.y_center - hh, self.y_center + hh
        
        # Punto más cercano en la caja al centro del círculo
        px = max(x_min, min(x_c, x_max))
        py = max(y_min, min(y_c, y_max))
        d2 = (x_c - px)**2 + (y_c - py)**2
        
        return d2 <= (radius**2)
    
    def distance(self, x_q: float, y_q: float) -> float:
        """Distancia euclidiana real (solo para usar si se necesita el valor exacto)"""
        return math.sqrt(self.distance_squared(x_q, y_q))
    
    def distance_squared(self, x_q: float, y_q: float) -> float:
        """Distacia euclidiana al cuadrado para optimizar el costo en CPU"""
        hw = self.width / 2.0
        hh = self.height / 2.0
        x_min, x_max = self.x_center - hw, self.x_center + hw
        y_min, y_max = self.y_center - hh, self.y_center + hh
        
        px = max(x_min, min(x_q, x_max))
        py = max(y_min, min(y_q, y_max))
        return (x_q - px)**2 + (y_q - py)**2

MAX_DEPTH = 20 # límite de profundidad para evitar RecursionError con datos duplicados
class Node:
    def __init__(self, boundary: BoundingBox, capacity: int, depth: int = 0) -> None:
        self.boundary = boundary
        self.capacity = capacity
        self.depth = depth
        self.points: List[Point] = []
        self.north_w: Optional['Node'] = None
        self.north_e: Optional['Node'] = None
        self.south_w: Optional['Node'] = None
        self.south_e: Optional['Node'] = None
    
    def insertar(self, point: Point) -> bool:
        if not self.boundary.contains_point(point):
            return False
        
        # Si aun hay espacio o si ya alcanzamos la profundidad máxima, y el nodo NO se ha dividido
        if (len(self.points) < self.capacity or self.depth >= MAX_DEPTH) and self.north_w is None:
            self.points.append(point)
            return True
        
        # El nodo está lleno y  NO se ha dividido se divide
        if self.north_w is None:
            s_quad: List[BoundingBox] = self._dividir()
            # Al crear hijos, aumentamos la profundidad
            self.north_w = Node(s_quad[0], self.capacity, self.depth + 1)
            self.north_e = Node(s_quad[1], self.capacity, self.depth + 1)
            self.south_w = Node(s_quad[2], self.capacity, self.depth + 1)
            self.south_e = Node(s_quad[3], self.capacity, self.depth + 1)
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
    
    def _dividir(self) -> List[BoundingBox]:
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
    
    def range_search(self, x_c: float, y_c: float, radius: float) -> List[Point]:
        results: List[Point] = []
        self._range_search(self.root, x_c, y_c, radius, results)
        return results
        
    def _range_search(self, node: Node, x_c: float, y_c: float, radius: float, results: List[Point]) -> None:
        if not node.boundary.intersects(x_c, y_c, radius):
            return
            
        if node.north_w is None:
            for p in node.points:
                d2 = (x_c - p.x)**2 + (y_c - p.y)**2
                if d2 <= radius**2:
                    results.append(p)
        else:
            self._range_search(node.north_w, x_c, y_c, radius, results)
            self._range_search(node.north_e, x_c, y_c, radius, results)
            self._range_search(node.south_w, x_c, y_c, radius, results)
            self._range_search(node.south_e, x_c, y_c, radius, results)
    
    def nearest_neighbor(self, x_query: float, y_query: float) -> Optional[Point]:
        campeon: List[Any] = [None, float('inf')]
        self._nearest_neighbor(self.root, x_query, y_query, campeon)
        return campeon[0]

    def _nearest_neighbor(self, node: Node, x_query: float, y_query: float, campeon: List[Any]) -> None:
        d = node.boundary.distance(x_query, y_query)
        if d >= campeon[1]:
            return
            
        if node.north_w is None:
            for p in node.points:
                d_punto = math.sqrt((x_query - p.x)**2 + (y_query - p.y)**2)
                if d_punto < campeon[1]:
                    campeon[0] = p
                    campeon[1] = d_punto
        else:
            hijos = [node.north_w, node.north_e, node.south_w, node.south_e]
            hijos.sort(key=lambda hijo: hijo.boundary.distance(x_query, y_query))
            
            for hijo in hijos:
                self._nearest_neighbor(hijo, x_query, y_query, campeon)

    def k_nearest_neighbors(self, x_query:float, y_query:float, k: int = 5) -> List[Point]:
        """
        Encuentra los K vecinos más cercanos
        Retorna una lista de puntos ordenados por cercanía
        """
        campeon: List[Tuple[float, Point]] = []
        self._k_nearest(self.root, x_query, y_query, k, campeon)
        # Ordenamos por distancia (menor a mayor) y extraemos solo los puntos
        campeon.sort(key=lambda x: x[0])
        return [p for d2, p in campeon]
        
    def _k_nearest(self, node: Node, x_q: float, y_q: float, k: int, campeon: List[Tuple[float, Point]]) -> None:
        d = node.boundary.distance_squared(x_q, y_q)
        
        # Si ya tenemos K vecinos, y la caja actual está más lejos 
        # que nuestro "peor" vecino actual, descartamos todo el subárbol
        if len(campeon) == k:
            worst_d2 = max(c[0] for c in campeon)
            if d >= worst_d2:
                return
        
        if node.north_w is None:
            for p in node.points:
                d2 = (x_q - p.x)**2 + (y_q - p.y)**2
                if len(campeon) < k:
                    campeon.append((d2, p))
                else:
                    worst_d2 = max(c[0] for c in campeon)
                    if d2 < worst_d2:
                        worst_idx = max(range(len(campeon)), key=lambda i: campeon[i][0])
                        campeon[worst_idx] = (d2, p)
        else:
            # Explorar primero los cuadrantes geométricamente más cercanos
            hijos = [node.north_w, node.north_e, node.south_w, node.south_e]
            hijos.sort(key=lambda h: h.boundary.distance_squared(x_q, y_q))
            for hijo in hijos:
                self._k_nearest(hijo, x_q, y_q, k, campeon)