import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Optional, Any

from Quadtree import Point, QuadTree, BoundingBox

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

# VISUALIZACIÓN

def visualizar_resultados(listaCoordenadas: List[Point], queryPoint: Point, radio: float, rango_quad: List[Point], nn_quad: Point):
    """Renderiza el mapa de la ciudad con una vista global y una vista con zoom."""
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
        ax.scatter(x_list, y_list, color=color_base, s=5, alpha=0.5, zorder=1)     
        # 2. Círculo de búsqueda
        patch = patches.Circle((queryPoint.x, queryPoint.y), radio, fill=False, color=color_circulo, linewidth=2, zorder=2)
        ax.add_patch(patch)
        # 3. Puntos encontrados en Range Search
        ax.scatter(x_rango, y_rango, color=color_rango, s=25, zorder=3)
        # 4. Punto de consulta (Centro)
        ax.scatter(queryPoint.x, queryPoint.y, color=color_query, marker='X', s=90, zorder=4)
        # 5. Vecino más cercano y su línea conectora
        ax.scatter(nn_quad.x, nn_quad.y, color=color_nn, s=60, zorder=5, edgecolor=color_texto, linewidth=0.5)
        ax.plot([nn_quad.x, queryPoint.x], [nn_quad.y, queryPoint.y], color=color_circulo, linestyle='--', linewidth=2, zorder=6)

        # Pintar los bordes del recuadro
        for spine in ax.spines.values():
            spine.set_color('#d8bfd8')

    # Configuración de textos
    ax1.set_title(f"Vista Global ({len(listaCoordenadas)} entregas)", color=color_texto, fontweight='bold')
    ax1.set_aspect('equal')
    
    ax2.set_title(f"Zoom: Radio de {radio}m", color=color_texto, fontweight='bold')
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

    rango_quad = tree.range_search(queryPoint.x, queryPoint.y, radio)
    rango_fb = range_search_fb(listaCoordenadas, queryPoint.x, queryPoint.y, radio)

    # Validaciones (Asserts)
    assert nn_quad.x == nn_fb.x
    assert nn_quad.y == nn_fb.y
    assert len(rango_quad) == len(rango_fb)
    
    set_quad = {(p.x, p.y) for p in rango_quad}
    set_fb = {(p.x, p.y) for p in rango_fb}
    assert set_quad == set_fb
    
    print("El QuadTree es geométricamente perfecto. Todos los asserts pasaron.")
    
    # Retornamos los datos
    return listaCoordenadas, queryPoint, radio, rango_quad, nn_quad

if __name__ == "__main__":
    # 1. Correr las pruebas y extraer los datos
    lista, qp, rad, rq, nn = test_correctness()
    
    # 2. Enviar los datos a la función de dibujo
    visualizar_resultados(lista, qp, rad, rq, nn) 