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
    quiebre_rq = None
    quiebre_nn = None

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
        
        # Capturar quiebre dinámico
        if quiebre_rq is None and promedio_rq_quad < promedio_rq_fb:
            quiebre_rq = N
        if quiebre_nn is None and promedio_nn_quad < promedio_nn_fb:
            quiebre_nn = N
        
    
        # ANÁLISIS EN CONSOLA Y PUNTO DE QUIEBRE
    
        print(f"N = {N:6} | Const. Quad: {tiempos_build[-1]:8.3f} ms | RQ Quad: {promedio_rq_quad:6.4f} ms | RQ FB: {promedio_rq_fb:6.4f} ms")
        
        if not quiebre_encontrado and promedio_rq_quad < promedio_rq_fb:
            print(f"  ---> PUNTO DE QUIEBRE: A partir de N={N}, QuadTree supera a la Fuerza Bruta.")
            quiebre_encontrado = True


    # VISUALIZACIÓN DE RESULTADOS LOGARÍTMICA

    print("-" * 75)
    print("Generando gráficas de rendimiento...")
    
    # Paleta de colores
    color_quad = '#9b59b6'  # Amatista / Morado vibrante
    color_fb = '#ff66b2'    # Rosa chicle 
    color_texto = '#4a235a' # Morado oscuro
    fondo = '#fff0f5'       # Lavender blush 
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(fondo)
    
    # Gráfica 1: Range Search
    ax1.set_facecolor('white')
    ax1.plot(tamanos, tiempos_rq_quad, label='QuadTree $\mathcal{O}(\log N + K)$', color=color_quad, marker='o', linewidth=2.5)
    ax1.plot(tamanos, tiempos_rq_fb, label='Fuerza Bruta $\mathcal{O}(N)$', color=color_fb, marker='x', linewidth=2.5)
    # visualización punto de quiebre
    if quiebre_rq:
        ax1.axvline(x=quiebre_rq, color='gray', linestyle=':', alpha=0.8)
        ax1.text(quiebre_rq * 1.1, min(tiempos_rq_quad), f'← Quiebre (N={quiebre_rq})', color='dimgray', fontsize=9)

    ax1.set_title('Búsqueda por Rango (500m)', color=color_texto, fontweight='bold')
    ax1.set_xlabel('Cantidad de Puntos (N)', color=color_texto)
    ax1.set_ylabel('Tiempo Promedio (ms)', color=color_texto)
    ax1.set_xscale('log') 
    ax1.set_yscale('log') 
    ax1.grid(True, which="both", ls="--", alpha=0.4, color='#d8bfd8') # Grid 
    ax1.legend(facecolor=fondo, edgecolor='#d8bfd8')

    # Gráfica 2: Nearest Neighbor
    ax2.set_facecolor('white')
    ax2.plot(tamanos, tiempos_nn_quad, label='QuadTree $\mathcal{O}(\log N)$', color=color_quad, marker='o', linewidth=2.5)
    ax2.plot(tamanos, tiempos_nn_fb, label='Fuerza Bruta $\mathcal{O}(N)$', color=color_fb, marker='x', linewidth=2.5)
    # visualización punto de quiebre
    if quiebre_nn:
        ax2.axvline(x=quiebre_nn, color='gray', linestyle=':', alpha=0.8)
        ax2.text(quiebre_nn * 1.1, min(tiempos_nn_quad), f'← Quiebre (N={quiebre_nn})', color='dimgray', fontsize=9)
    
    ax2.set_title('Vecino Más Cercano', color=color_texto, fontweight='bold')
    ax2.set_xlabel('Cantidad de Puntos (N)', color=color_texto)
    ax2.set_ylabel('Tiempo Promedio (ms)', color=color_texto)
    ax2.set_xscale('log') 
    ax2.set_yscale('log') 
    ax2.grid(True, which="both", ls="--", alpha=0.4, color='#d8bfd8')
    ax2.legend(facecolor=fondo, edgecolor='#d8bfd8')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    ejecutar_benchmarking()