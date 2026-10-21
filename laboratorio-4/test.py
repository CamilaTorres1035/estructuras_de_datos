import random
random.seed(42) # Reproducibilidad para que los datos y consultas sean idénticos en cada ejecución
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Optional, Any

from Quadtree import Point, QuadTree, BoundingBox

def edge_cases():
    """Pruebas de robustez ante casos borde"""
    boundary = BoundingBox(5000, 5000, 10000, 10000)
    tree = QuadTree(boundary)
    # árbol vacío
    assert tree.nearest_neighbor(100, 100) is None
    assert tree.k_nearest_neighbors(100, 100, 5) == []
    assert tree.range_search(100, 100, 500) == []
    # radio 0 y fuera del mapa
    p = Point(100, 100)
    tree.insertar(p)
    assert len(tree.range_search(100, 100, 0)) == 1
    assert tree.range_search(99999, 99999, 10) == []
    # puntos duplicados
    for _ in range(10): tree.insertar(Point(5000, 5000))
    assert len(tree.range_search(5000, 5000, 10)) == 10
    assert len(tree.k_nearest_neighbors(5000, 5000, 5)) == 5
    
    print("Casos borde superados")

# ALGORITMOS DE REFERENCIA (Fuerza Bruta)

def range_search_fb(puntos: List[Point], x_c: float, y_c: float, radius: float) -> List[Point]:
    results: List[Point] = []
    r2 = radius**2
    for p in puntos:
        d2 = (x_c-p.x)**2 + (y_c-p.y)**2
        if d2 <= r2:
            results.append(p)
    return results

def nearest_neighbor_fb(puntos: List[Point], x_query: float, y_query: float) -> Optional[Point]:
    campeon: List[Any] = [None, float('inf')]
    for p in puntos:
        d2 = (x_query-p.x)**2 + (y_query-p.y)**2
        if d2 < campeon[1]:
            campeon[1] = d2
            campeon[0] = p
    return campeon[0]

def k_nearest_fb(puntos: List[Point], x_query: float, y_query: float, k: int = 5) -> List[Point]:
    distancias = []
    for p in puntos:
        d2 = (x_query - p.x)**2 + (y_query - p.y)**2
        distancias.append((d2, p))
    distancias.sort(key=lambda x: x[0])
    return [p for d2, p in distancias[:k]]

# VISUALIZACIÓN

def visualizar_resultados(listaCoordenadas: List[Point], queryPoint: Point, radio: float, rango_quad: List[Point], nn_quad: Point, knn_quad: List[Point]):
    """Renderiza el mapa de la ciudad con una vista global y una vista con zoom"""
    # Paleta de colores
    fondo_figura = '#fff0f5'      
    color_base = '#e8daef'        # Lila pastel para la ciudad
    color_circulo = '#ff66b2'     # Rosa chicle
    color_rango = '#9b59b6'       # Amatista (Paquetes encontrados)
    color_query = "#ff0088"       # Deep pink (Tu ubicación)
    color_nn = "#e1b60b"          # Dorado (Vecino más cercano)
    color_texto = '#4a235a'       # Morado oscuro

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor(fondo_figura)
    
    x_list = [p.x for p in listaCoordenadas]
    y_list = [p.y for p in listaCoordenadas]
    x_rango = [p.x for p in rango_quad]
    y_rango = [p.y for p in rango_quad]
    
    for ax in (ax1, ax2):
        ax.set_facecolor('white')
        # 1. Fondo de ciudad
        ax.scatter(x_list, y_list, color=color_base, s=5, alpha=0.5, zorder=1, label='Puntos del Dataset')
        # 2. Círculo de búsqueda
        patch = patches.Circle((qp.x, qp.y), rad, fill=False, color=color_circulo, linewidth=2, zorder=2, label=f'Radio de Búsqueda ({rad}m)')
        ax.add_patch(patch)
        # 3. Puntos encontrados en Range Search
        ax.scatter(x_rango, y_rango, color=color_rango, s=25, zorder=3, label='Puntos en Rango (Range Search)')
        # 4. Punto de consulta (Centro)
        ax.scatter(qp.x, qp.y, color=color_query, marker='X', s=90, zorder=4, label='Punto de Consulta')
        # 5. Dibujar K-vecinos.
        for nn in knn_quad:
            is_primary = (nn.x == nn_quad.x and nn.y == nn_quad.y)
            size = 90 if is_primary else 45
            lw = 2.5 if is_primary else 1.0
            alpha = 1.0 if is_primary else 0.6
            
            ax.scatter(nn.x, nn.y, color=color_nn, s=60, zorder=5, edgecolor=color_texto, linewidth=0.5, label='Vecino Más Cercano (1-NN)')
            ax.plot([nn.x, qp.x], [nn.y, qp.y], color=color_circulo, linestyle='--', linewidth=1.5, zorder=4)

        # Pintar los bordes del recuadro
        for spine in ax.spines.values():
            spine.set_color('#d8bfd8')

    # Configuración de textos
    ax1.set_title(f"Vista Global ({len(listaCoordenadas)} entregas)", color=color_texto, fontweight='bold')
    ax1.set_aspect('equal')
    
    ax2.set_title(f"Zoom: Radio de {radio}m y K-Vecinos", color=color_texto, fontweight='bold')
    ax2.set_aspect('equal')
    margen_zoom = radio * 1.5
    ax2.set_xlim(queryPoint.x - margen_zoom, queryPoint.x + margen_zoom)
    ax2.set_ylim(queryPoint.y - margen_zoom, queryPoint.y + margen_zoom)
    
    plt.tight_layout()
    plt.show()

# PRUEBAS (Unit Testing)

def test_correctness():
    """Genera datos, ejecuta pruebas de correctitud y retorna los resultados para visualización."""
    RANGO_MAXIMO = 10000
    CANTIDAD_PUNTOS = 10000
    K = 5

    listaCoordenadas: List[Point] = []
    boundary = BoundingBox(RANGO_MAXIMO/2, RANGO_MAXIMO/2, RANGO_MAXIMO, RANGO_MAXIMO)
    tree = QuadTree(boundary)

    # Generación de datos
    for _ in range(CANTIDAD_PUNTOS):
        x_rand = random.uniform(0, RANGO_MAXIMO)
        y_rand = random.uniform(0, RANGO_MAXIMO)
        p = Point(x_rand, y_rand)
        listaCoordenadas.append(p)
        tree.insertar(p)

    queryPoint = Point(random.uniform(0, RANGO_MAXIMO), random.uniform(0, RANGO_MAXIMO))
    radio = 500.0
    
    nn_quad = tree.nearest_neighbor(queryPoint.x, queryPoint.y)
    nn_fb = nearest_neighbor_fb(listaCoordenadas, queryPoint.x, queryPoint.y)
    
    knn_quad = tree.k_nearest_neighbors(queryPoint.x, queryPoint.y, K)
    knn_fb = k_nearest_fb(listaCoordenadas, queryPoint.x, queryPoint.y, K)

    rango_quad = tree.range_search(queryPoint.x, queryPoint.y, radio)
    rango_fb = range_search_fb(listaCoordenadas, queryPoint.x, queryPoint.y, radio)

    # Validaciones (Asserts)
    assert nn_quad.x == nn_fb.x and nn_quad.y == nn_fb.y, "Fallo en NN único"
    assert len(knn_quad) == len(knn_fb), "Fallo en cantidad de KNN"
    for p_q, p_fb in zip(knn_quad, knn_fb):
        assert p_q.x == p_fb.x and p_q.y == p_fb.y, "Fallo en coordenadas KNN"
        
    assert len(rango_quad) == len(rango_fb)
    set_quad = {(p.x, p.y) for p in rango_quad}
    set_fb = {(p.x, p.y) for p in rango_fb}
    assert set_quad == set_fb
    
    print("El QuadTree es geométricamente perfecto. Todos los asserts pasaron.")
    
    # Retornamos los datos
    return listaCoordenadas, queryPoint, radio, rango_quad, nn_quad, knn_quad

if __name__ == "__main__":
    edge_cases()
    lista, qp, rad, rq, nn, knn = test_correctness()
    visualizar_resultados(lista, qp, rad, rq, nn, knn)
