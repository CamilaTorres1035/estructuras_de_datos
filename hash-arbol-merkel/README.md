# Hashes y Árboles de Merkle

## Requisitos Generales del Entorno

* **Lenguaje:** Python 3.10 o superior.
* **Dependencias principales:** Módulos estándar de Python (`hashlib`, `multiprocessing`, `time`, `json`) y entorno Jupyter Notebook (`jupyter` / `notebook`).

## Descripción

En este módulo se abordan la solución del reto 1 relacionado con hashes y árboles de Merkle usando la búsqueda por fuerza bruta optimizada de claves numéricas de 8 dígitos a partir de su hash SHA-256 y la construcción e inspección jerárquica de un **Árbol de Merkle** (*Merkle Tree*) para la verificación de integridad de transacciones.

### Poblemas Resueltos

1. **Optimización de Búsqueda de clave a partir de su hash:**
   * **Formateo Directo a Bytes:** Se sustituye la conversión lenta `str(i).zfill(8).encode()` por formateo nativo en bytes (`b"%08d"`), eliminando la sobrecarga en recolección de basura e I/O de cadenas.
   * **Paralelización Multiproceso:** Se distribuye el espacio total de búsqueda ($100{,}000{,}000$ de combinaciones posibles, desde `00000000` hasta `99999999`) entre todos los núcleos de la CPU usando `multiprocessing.Pool` y `starmap`.
   * **Reducción de Tiempos:** Se logra reducir el tiempo de búsqueda en peor escenario de aproximadamente ~5 minutos a ~18 segundos (probado en CPU de 12 núcleos).

2. **Construcción e Inspección de Árbol de Merkle:**
   * **Serialización Determinista:** Implementación de `json.dumps` con ordenamiento de claves (`sort_keys=True`) para garantizar consistencia en la generación de hashes por transacción.
   * **Estructuración Jerárquica:** Agrupamiento y concatenación de pares de hashes hoja hasta converger en una única raíz (*Merkle Root*).
   * **Manejo de Nodos Impares:** Promoción directa del nodo remanente al siguiente nivel cuando un nivel cuenta con un número impar de nodos.

## Archivos del Repositorio

| Archivo | Descripción |
| :--- | :--- |
| `busqueda.py` | Script interactivo para encontrar la clave de 8 dígitos que genera un hash SHA-256 objetivo utilizando multiprocessing y optimización a nivel de bytes. |
| `rendimiento.py` | Módulo de benchmark comparativo que evalúa la aceleración ($\text{speedup}$) y la tasa de hashes por segundo ($\text{H/s}$) enfrentando la versión mononúcleo tradicional contra la optimizada. |
| `problemasHash.ipynb` | Notebook interactivo con la resolución secuencial inicial de la búsqueda de claves y la implementación/dibujado completo del Árbol de Merkle. |

## Benchmark y Evidencia de Rendimiento

El script `rendimiento.py` evalúa la eficiencia de la búsqueda paralela mediante pruebas comparativas en peor caso:

![Comparativa de Búsqueda Hash](../img/comparativaBusquedaHash.png)
