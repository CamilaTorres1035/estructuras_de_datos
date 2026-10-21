import time
import random
import statistics
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

def k_nearest_fb(puntos: List[Point], x_query: float, y_query: float, k: int = 5) -> List[Point]:
    # esta implementación es O(N log N) por el sort NO O(N)
    distancias = []
    for p in puntos:
        d2 = (x_query - p.x)**2 + (y_query - p.y)**2
        distancias.append((d2, p))
    distancias.sort(key=lambda x: x[0])
    return [p for d2, p in distancias[:k]]

# CONFIGURACIÓN DEL EXPERIMENTO
def ejecutar_benchmarking():
    RANGO_MAXIMO = 10000
    RADIO_BUSQUEDA = 500.0
    NUM_CONSULTAS = 100 # Tamaño del lote para promediar
    K = 5
    REPETICIONES = 8
    
    # Conservamos los pequeños para ver el quiebre y agregamos gigantes para el escalamiento
    tamanos = [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]
    
    medianas_build = []
    medianas_rq_quad, medianas_rq_fb = [], []
    medianas_nn_quad, medianas_nn_fb = [], []
    medianas_knn_quad, medianas_knn_fb = [], []

    quiebre_rq = None
    quiebre_nn = None
    quiebre_knn = None

    print("Iniciando Benchmarking...")
    print(f"Mapa: {RANGO_MAXIMO} x {RANGO_MAXIMO} m | Radio de búsqueda: {RADIO_BUSQUEDA} m | K = {K}")
    print("-" * 75)


    # CICLO PRINCIPAL DE EVALUACIÓN
    for N in tamanos:
        t_build_runs, t_rq_quad_runs, t_rq_fb_runs = [], [], []
        t_nn_quad_runs, t_nn_fb_runs = [], []
        t_knn_quad_runs, t_knn_fb_runs = [], []
        
        boundary = BoundingBox(RANGO_MAXIMO/2, RANGO_MAXIMO/2, RANGO_MAXIMO, RANGO_MAXIMO)
        
        for _ in range(REPETICIONES):
            # Generar los N puntos aleatorios
            lista_puntos = []
            for _ in range(N):
                x_rand = random.uniform(0, RANGO_MAXIMO)
                y_rand = random.uniform(0, RANGO_MAXIMO)
                p = Point(x_rand, y_rand)
                lista_puntos.append(p)
        
            # Medir tiempo de Construcción del QuadTree
            t_inicio = time.perf_counter()
            tree = QuadTree(boundary)
            for p in lista_puntos:
                tree.insertar(p)
            t_fin = time.perf_counter()

            t_build_runs.append((t_fin - t_inicio) * 1000)

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
            t_rq_quad_runs.append(promedio_rq_quad)

            t_inicio = time.perf_counter()
            for q in consultas:
                range_search_fb(lista_puntos, q.x, q.y, RADIO_BUSQUEDA)
            t_fin = time.perf_counter()
            promedio_rq_fb = ((t_fin - t_inicio) * 1000) / NUM_CONSULTAS
            t_rq_fb_runs.append(promedio_rq_fb)

            # COMPARACIÓN: Nearest Neighbor
            t_inicio = time.perf_counter()
            for q in consultas:
                tree.nearest_neighbor(q.x, q.y)
            t_fin = time.perf_counter()
            promedio_nn_quad = ((t_fin - t_inicio) * 1000) / NUM_CONSULTAS
            t_nn_quad_runs.append(promedio_nn_quad)

            t_inicio = time.perf_counter()
            for q in consultas:
                nearest_neighbor_fb(lista_puntos, q.x, q.y)
            t_fin = time.perf_counter()
            promedio_nn_fb = ((t_fin - t_inicio) * 1000) / NUM_CONSULTAS
            t_nn_fb_runs.append(promedio_nn_fb)
            
            # COMPARACIÓN: K-NN
            t0 = time.perf_counter()
            for q in consultas: tree.k_nearest_neighbors(q.x, q.y, K)
            t_knn_quad_runs.append(((time.perf_counter() - t0) * 1000) / NUM_CONSULTAS)

            t0 = time.perf_counter()
            for q in consultas: k_nearest_fb(lista_puntos, q.x, q.y, K)
            t_knn_fb_runs.append(((time.perf_counter() - t0) * 1000) / NUM_CONSULTAS)
        
        # CÁLCULO DE MEDIANAS
        medianas_build.append(statistics.median(t_build_runs))
        medianas_rq_quad.append(statistics.median(t_rq_quad_runs)); medianas_rq_fb.append(statistics.median(t_rq_fb_runs))
        medianas_nn_quad.append(statistics.median(t_nn_quad_runs)); medianas_nn_fb.append(statistics.median(t_nn_fb_runs))
        medianas_knn_quad.append(statistics.median(t_knn_quad_runs)); medianas_knn_fb.append(statistics.median(t_knn_fb_runs))
        
        # Detección de cruces
        if quiebre_rq is None and medianas_rq_quad[-1] < medianas_rq_fb[-1]: quiebre_rq = N
        if quiebre_nn is None and medianas_nn_quad[-1] < medianas_nn_fb[-1]: quiebre_nn = N
        if quiebre_knn is None and medianas_knn_quad[-1] < medianas_knn_fb[-1]: quiebre_knn = N
        
        print(f"N={N:6} | Build: {medianas_build[-1]:7.3f} ms | "
              f"RQ (Q/FB): {medianas_rq_quad[-1]:.4f}/{medianas_rq_fb[-1]:.4f} | "
              f"NN (Q/FB): {medianas_nn_quad[-1]:.4f}/{medianas_nn_fb[-1]:.4f} | "
              f"KNN (Q/FB): {medianas_knn_quad[-1]:.4f}/{medianas_knn_fb[-1]:.4f}")
        
    
    # ANÁLISIS EN CONSOLA Y PUNTO DE QUIEBRE
    print("-" * 95)
    print(f"PUNTO DE QUIEBRE Range Search: N ≈ {quiebre_rq}")
    print(f"PUNTO DE QUIEBRE NN Único: N ≈ {quiebre_nn}")
    print(f"PUNTO DE QUIEBRE KNN (K={K}): N ≈ {quiebre_knn} (Tarda más en superar a FB por el overhead de mantener los K mejores)")


    # VISUALIZACIÓN DE RESULTADOS LOGARÍTMICA
    color_quad = '#9b59b6'  # Amatista / Morado vibrante
    color_fb = '#ff66b2'    # Rosa chicle 
    color_texto = '#4a235a' # Morado oscuro
    fondo = '#fff0f5'       # Lavender blush
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor(fondo)
    
    def configurar_eje(ax, titulo, t_quad, t_fb, quiebre):
        ax.set_facecolor('white')
        ax.plot(tamanos, t_quad, label='QuadTree', color=color_quad, marker='o', linewidth=2.5)
        ax.plot(tamanos, t_fb, label='Fuerza Bruta', color=color_fb, marker='x', linewidth=2.5)
        if quiebre:
            ax.axvline(x=quiebre, color='gray', linestyle=':', alpha=0.8)
            ax.text(quiebre * 1.1, min(t_quad), f'← Quiebre (N={quiebre})', color='dimgray', fontsize=9)
        ax.set_title(titulo, color=color_texto, fontweight='bold')
        ax.set_xlabel('Cantidad de Puntos (N)', color=color_texto)
        ax.set_ylabel('Tiempo Mediano por Consulta (ms)', color=color_texto)
        ax.set_xscale('log'); ax.set_yscale('log')
        ax.grid(True, which="both", ls="--", alpha=0.4, color='#d8bfd8')
        ax.legend(facecolor=fondo, edgecolor='#d8bfd8')
    
    configurar_eje(ax1, 'Búsqueda por Rango (500 m)', medianas_rq_quad, medianas_rq_fb, quiebre_rq)
    configurar_eje(ax2, 'Vecino Más Cercano (NN único)', medianas_nn_quad, medianas_nn_fb, quiebre_nn)
    configurar_eje(ax3, f'K-Vecinos Más Cercanos (K={K})', medianas_knn_quad, medianas_knn_fb, quiebre_knn)
    
    fig.suptitle(
        f'Rendimiento comparativo | Mediana de {REPETICIONES} corridas, '
        f'{NUM_CONSULTAS} consultas por corrida | Mapa 10 km × 10 km',
        color=color_texto, fontsize=13, fontweight='bold'
    )
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    ejecutar_benchmarking()