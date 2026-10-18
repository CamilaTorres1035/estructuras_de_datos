import time
import random
import matplotlib.pyplot as plt
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

# CONFIGURACIÓN DEL EXPERIMENTO
def ejecutar_benchmarking():
    RANGO_MAXIMO = 10000
    RADIO_BUSQUEDA = 500.0
    NUM_CONSULTAS = 100 # Tamaño del lote para promediar
    
    # Conservamos los pequeños para ver el quiebre y agregamos gigantes para el escalamiento
    tamanos = [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]
    
    tiempos_build = []
    tiempos_rq_quad = []
    tiempos_rq_fb = []
    tiempos_nn_quad = []
    tiempos_nn_fb = []

    quiebre_encontrado = False

    print("Iniciando Benchmarking...")
    print("-" * 75)


    # CICLO PRINCIPAL DE EVALUACIÓN
    for N in tamanos:
        # Generar los N puntos aleatorios
        lista_puntos = []
        for _ in range(N):
            x_rand = random.uniform(0, RANGO_MAXIMO)
            y_rand = random.uniform(0, RANGO_MAXIMO)
            p = Point(x_rand, y_rand)
            lista_puntos.append(p)
        
        # Medir tiempo de Construcción del QuadTree
        boundary = BoundingBox(RANGO_MAXIMO/2, RANGO_MAXIMO/2, RANGO_MAXIMO, RANGO_MAXIMO)
        
        t_inicio = time.perf_counter()
        tree = QuadTree(boundary)
        for p in lista_puntos:
            tree.insertar(p)
        t_fin = time.perf_counter()
        
        tiempos_build.append((t_fin - t_inicio) * 1000)

        # Generar puntos de consulta comunes 
        consultas = []
        for _ in range(NUM_CONSULTAS):
            x_rand = random.uniform(0, RANGO_MAXIMO)
            y_rand = random.uniform(0, RANGO_MAXIMO)
            p = Point(x_rand, y_rand)
            consultas.append(p)

        # COMPARACIÓN: Range Search
        t_inicio = time.perf_counter()
        for q in consultas:
            tree.range_search(q.x, q.y, RADIO_BUSQUEDA)
        t_fin = time.perf_counter()
        promedio_rq_quad = ((t_fin - t_inicio) * 1000) / NUM_CONSULTAS
        tiempos_rq_quad.append(promedio_rq_quad)

        t_inicio = time.perf_counter()
        for q in consultas:
            range_search_fb(lista_puntos, q.x, q.y, RADIO_BUSQUEDA)
        t_fin = time.perf_counter()
        promedio_rq_fb = ((t_fin - t_inicio) * 1000) / NUM_CONSULTAS
        tiempos_rq_fb.append(promedio_rq_fb)

        # COMPARACIÓN: Nearest Neighbor
        t_inicio = time.perf_counter()
        for q in consultas:
            tree.nearest_neighbor(q.x, q.y)
        t_fin = time.perf_counter()
        promedio_nn_quad = ((t_fin - t_inicio) * 1000) / NUM_CONSULTAS
        tiempos_nn_quad.append(promedio_nn_quad)
        
        t_inicio = time.perf_counter()
        for q in consultas:
            nearest_neighbor_fb(lista_puntos, q.x, q.y)
        t_fin = time.perf_counter()
        promedio_nn_fb = ((t_fin - t_inicio) * 1000) / NUM_CONSULTAS
        tiempos_nn_fb.append(promedio_nn_fb)
        
    
        # ANÁLISIS EN CONSOLA Y PUNTO DE QUIEBRE
    
        print(f"N = {N:6} | Const. Quad: {tiempos_build[-1]:8.3f} ms | RQ Quad: {promedio_rq_quad:6.4f} ms | RQ FB: {promedio_rq_fb:6.4f} ms")
        
        if not quiebre_encontrado and promedio_rq_quad < promedio_rq_fb:
            print(f"  ---> PUNTO DE QUIEBRE: A partir de N={N}, QuadTree supera a la Fuerza Bruta.")
            quiebre_encontrado = True


    # VISUALIZACIÓN DE RESULTADOS LOGARÍTMICA

    print("-" * 75)
    print("Generando gráficas de rendimiento...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gráfica 1: Range Search
    ax1.plot(tamanos, tiempos_rq_quad, label='QuadTree $\mathcal{O}(\log N)$', color='blue', marker='o')
    ax1.plot(tamanos, tiempos_rq_fb, label='Fuerza Bruta $\mathcal{O}(N)$', color='red', marker='x')
    ax1.set_title('Búsqueda por Rango (500m)')
    ax1.set_xlabel('Cantidad de Puntos (N)')
    ax1.set_ylabel('Tiempo Promedio (ms)')
    ax1.set_xscale('log') # Escala Logarítmica X
    ax1.set_yscale('log') # Escala Logarítmica Y
    ax1.grid(True, which="both", ls="--", alpha=0.5)
    ax1.legend()

    # Gráfica 2: Nearest Neighbor
    ax2.plot(tamanos, tiempos_nn_quad, label='QuadTree $\mathcal{O}(\log N)$', color='blue', marker='o')
    ax2.plot(tamanos, tiempos_nn_fb, label='Fuerza Bruta $\mathcal{O}(N)$', color='red', marker='x')
    ax2.set_title('Vecino Más Cercano')
    ax2.set_xlabel('Cantidad de Puntos (N)')
    ax2.set_ylabel('Tiempo Promedio (ms)')
    ax2.set_xscale('log') # Escala Logarítmica X
    ax2.set_yscale('log') # Escala Logarítmica Y
    ax2.grid(True, which="both", ls="--", alpha=0.5)
    ax2.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    ejecutar_benchmarking()