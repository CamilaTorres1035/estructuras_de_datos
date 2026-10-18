import random

from Quadtree import Point, QuadTree, BoundingBox
from typing import List, Optional, Any
import matplotlib.pyplot as plt
import matplotlib.patches as patches

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

def test_correctness():
    """ test de correctitud para evaluar correctitud geometrica del QuadTree"""
    RANGO_MAXIMO = 10000
    CANTIDAD_PUNTOS = 1000

    listaCoordenadas: List[Point] = []
    boundary = BoundingBox(RANGO_MAXIMO/2, RANGO_MAXIMO/2, RANGO_MAXIMO, RANGO_MAXIMO)
    tree = QuadTree(boundary)

    for _ in range(CANTIDAD_PUNTOS):
        x_rand = random.uniform(0, RANGO_MAXIMO)
        y_rand = random.uniform(0, RANGO_MAXIMO)
        p = Point(x_rand, y_rand)
        listaCoordenadas.append(p)
        tree.insertar(p)

    queryPoint = Point(random.uniform(0, RANGO_MAXIMO), random.uniform(0, RANGO_MAXIMO))
    
    # 1. Ejecutar búsquedas NN
    nn_quad = tree.nearest_neighbor(queryPoint.x, queryPoint.y)
    nn_fb = nearest_neighbor(listaCoordenadas, queryPoint.x, queryPoint.y)

    # 2. Afirmar que son el mismo punto
    assert nn_quad.x == nn_fb.x
    assert nn_quad.y == nn_fb.y
    
    # 3. Ejecutar búsquedas por rango
    radio = 500.0
    rango_quad = tree.range_search(queryPoint.x, queryPoint.y, radio)
    rango_fb = range_search(listaCoordenadas, queryPoint.x, queryPoint.y, radio)

    # 4. Afirmar que encontraron la misma cantidad
    assert len(rango_quad) == len(rango_fb)

    # 5. Afirmar que son exactamente los mismos puntos (ignorando el orden)
    set_quad = {(p.x, p.y) for p in rango_quad}
    set_fb = {(p.x, p.y) for p in rango_fb}
    assert set_quad == set_fb
    
    print("El QuadTree es geométricamente perfecto. Todos los asserts pasaron.")
    
    def visualizar_resultados():
        fig, ax = plt.subplots(figsize=(10, 10))
        
        x_list = [p.x for p in listaCoordenadas]
        y_list = [p.y for p in listaCoordenadas]
        
        ax.scatter(x_list, y_list, color='lightgray', s=10)     
        ax.scatter(queryPoint.x, queryPoint.y, color='red', marker='X', s=50)
        
        patch = patches.Circle((queryPoint.x, queryPoint.y), radio, fill=False, color='blue')
        ax.add_patch(patch)
        
        x_list = [p.x for p in rango_quad]
        y_list = [p.y for p in rango_quad]
        ax.scatter(x_list, y_list, color='green', s=15)
        
        ax.scatter(nn_quad.x, nn_quad.y, color='orange', s=30)
        ax.plot([nn_quad.x, queryPoint.x], [nn_quad.y, queryPoint.y], color='red', linestyle='--')
        
        plt.show()
    
    visualizar_resultados()

test_correctness()