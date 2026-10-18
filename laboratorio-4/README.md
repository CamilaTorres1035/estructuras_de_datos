# Laboratorio: Implementación de Árbol QuadTree Bidimensional

**Estudiante:** Maria Camila Torres Chica

## Requisitos Generales del Entorno

* **Lenguaje:** Python 3.10 o superior.
* **Dependencias principales:** Módulos estándar de Python (`math`, `time`, `random`), y `matplotlib` para la generación de gráficas y renderizado espacial.

## Descripción del Proyecto

Este proyecto implementa un árbol **QuadTree bidimensional** desde cero, diseñado para optimizar un sistema de logística de entregas en una ciudad. El sistema gestiona las coordenadas espaciales estáticas de 10.000 puntos de entrega y evalúa la eficiencia de esta estructura jerárquica frente a un enfoque de **fuerza bruta** (búsqueda en listas).

### Preguntas Logísticas Resueltas

El sistema está diseñado para responder eficientemente a dos requerimientos críticos:

1. **Búsqueda por Rango (Range Search):** ¿Qué puntos de entrega están a un radio exacto de 500 metros desde un punto de consulta dado?
2. **Vecino Más Cercano (Nearest Neighbor):** ¿Cuál es el punto de entrega más cercano a una ubicación dada?

## Diseño Algorítmico y Complejidad Espacial

### 1. Construcción del Árbol QuadTree

El árbol se construye dividiendo recursivamente el espacio 2D en regiones. Cada nodo representa una caja delimitadora (*Bounding Box*). Cuando un nodo supera su capacidad máxima, el espacio se divide en cuatro cuadrantes (noroeste, noreste, suroeste, sureste). Esto permite organizar los puntos según su posición espacial y preparar el terreno para la poda.

### 2. Búsqueda en Radio $\mathcal{O}(\log N + K)$

Para encontrar puntos dentro del radio de 500m:

* Se calcula la intersección entre el círculo de búsqueda y la caja del nodo.
* Si una región está completamente fuera del radio, se poda (se ignora esa rama entera).
* Introduce el concepto de *Complejidad Sensible a la Salida*: El tiempo depende logarítmicamente del total de datos ($N$), más un factor ($K$) proporcional a la cantidad de paquetes efectivamente encontrados dentro del radio.

### 3. Vecino Más Cercano $\mathcal{O}(\log N)$

Se realiza una búsqueda priorizando los cuadrantes que están geométricamente más cerca del punto de consulta. Se mantiene un registro de la distancia del "campeón" actual, lo que permite descartar rápidamente cuadrantes enteros cuya distancia mínima a la frontera sea mayor que la distancia del campeón encontrado.

## Análisis de Rendimiento (Benchmarking)

Para garantizar resultados empíricos rigurosos, se realizaron pruebas de estrés escalando el tamaño del conjunto de datos en una escala logarítmica: $N \in \{10, 50, 100, 500, 1.000, 5.000, 10.000, 50.000, 100.000\}$. En cada $N$, se promedió el tiempo de 100 consultas simultáneas.

A partir de los experimentos realizados, se determinó empíricamente que **el punto de quiebre exacto es $N = 50$**.

* En $N = 10$, la fuerza bruta es más rápida ($0.0034\text{ ms}$ vs $0.0062\text{ ms}$) debido a que recorrer arreglos contiguos en memoria tiene menos fricción que el costo de instanciar clases y evaluar cajas en el QuadTree.
* **En $N = 50$**, ocurre el cruce: el QuadTree ($0.0102\text{ ms}$) supera a la fuerza bruta ($0.0141\text{ ms}$). A partir de este umbral, el ahorro de tiempo generado por la poda espacial amortiza completamente el costo estructural del árbol.

### Desempeño a Escala Logística ($N = 10.000$)

A medida que el número de puntos aumenta, la fuerza bruta se vuelve insostenible debido a su naturaleza $\mathcal{O}(N)$. En la escala de 10.000 entregas:

* La **Fuerza Bruta** degradó su rendimiento a $1.7725\text{ ms}$ por consulta de rango.
* El **QuadTree** mantuvo su latencia en apenas $0.1171\text{ ms}$.
Esto representa una aceleración superior a **$15\times$** frente a enfoques convencionales.

## Conclusión

El QuadTree es una estructura óptima para consultas espaciales en dos dimensiones. Su construcción tiene un costo de inicialización de $59.28\text{ ms}$ para 10.000 puntos, pero este costo único se compensa drásticamente cuando se realizan múltiples consultas. Aunque la fuerza bruta es suficiente para conjuntos minúsculos ($N < 50$), el QuadTree es la única alternativa viable para sistemas de logística en tiempo real con volúmenes de datos urbanos.

## Archivos del Repositorio

| Archivo | Descripción |
| :--- | :--- |
| `Quadtree.py` | Implementación nativa de la estructura de datos, clases `Point`, `Node` y `BoundingBox`. Lógica matemática de inserción y búsquedas (completamente tipada y sin librerías externas). |
| `test.py` | Pruebas unitarias (*asserts*) de correctitud geométrica y renderizado espacial de la metrópolis. Emplea una vista dual (Global y Zoom) para certificar las intersecciones. |
| `analisis.py` | Suite de benchmarking por lotes. Evalúa los algoritmos, captura los puntos de quiebre estadísticos y renderiza las gráficas logarítmicas de rendimiento comparativo. |

## Evidencias (Capturas de Pantalla)

### 1. Verificación Visual de Consultas Espaciales

*(A la izquierda: Mapeo de 10.000 entregas y la zona de consulta. A la derecha: Ampliación al radio de 500m mostrando paquetes encontrados, la ubicación central y el vecino más cercano conectado por vector).*
![Verificación Visual](/laboratorio-4/Gráficas/Figure_1.png)

### 2. Comparativa de Rendimiento y Punto de Quiebre ($N=50$)

*(Curvas de tiempo promedio: QuadTree vs Fuerza Bruta. Escala Log-Log denotando la divergencia de complejidad $\mathcal{O}(\log N)$ vs $\mathcal{O}(N)$).*
![Gráficas de Rendimiento](/laboratorio-4/Gráficas/Figure_2.png)

### 3. Registro en Consola del Benchmarking

*(Métricas en milisegundos y detección algorítmica del umbral en N=50).*
![Métricas en Consola](/laboratorio-4/Gráficas/Resultados_Análisis.png)
