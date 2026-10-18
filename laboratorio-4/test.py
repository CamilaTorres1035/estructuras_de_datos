from Quadtree import Point
from typing import List, Optional, Any

listaCoordenadas: List[Point] = []

def range_search(puntos:List[Point], x_c:float, y_c:float, radius:float) -> List[Point]:
    results: List[Point] = []
    r2 = radius**2
    
    for p in puntos:
        d2 = (x_c-p.x)**2 + (y_c-p.y)**2
        if d2 <= r2:
            results.append(p)
    
    return results

def nearest_neighbor(puntos:List[Point], x_query:float, y_query:float) -> Optional[Point]:
    campeon: List[Any] = [None, float('inf')]
    
    for p in puntos:
        d2 = (x_query-p.x)**2 + (y_query-p.y)**2
        if d2 < campeon[1]:
            campeon[1] = d2
            campeon[0] = p
    
    return campeon[0]

