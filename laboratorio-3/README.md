# Sistema de Búsqueda y Organización: Árboles ABB y B+

## Requisitos Generales del Entorno

* **Lenguaje:** Python 3.11 o superior.
* **Dependencias principales:**

  * `Faker` (v40.39.0) para generación de datos sintéticos
  * `NumPy` (v2.5.3) para cálculos estadísticos
  * `SciPy` (v1.18.1) para análisis estadístico avanzado
  * `Matplotlib` (v3.11.2) para visualización de resultados
  * Módulos estándar: `random`, `bisect`, `time`, `math`, `gc`
  * Entorno Jupyter Notebook (`jupyter` / `notebook`)

## Descripción

Este proyecto realiza un **estudio experimental completo** sobre el comportamiento de tres estructuras de almacenamiento (Lista Nativa, Árbol Binario de Búsqueda - ABB, y Árbol B+) para gestionar una base de datos de estudiantes.

El objetivo principal es analizar **cómo escala el rendimiento** de cada estructura ante diferentes volúmenes de datos (N desde 10 hasta 100,000 registros), patrones de acceso (datos aleatorios vs. ordenados), y tipos de operaciones (búsquedas exitosas/fallidas, inserciones, listados ordenados y consultas por rango).

### Estructuras Implementadas

1. **Lista Nativa:** Búsqueda secuencial estándar O(N).
2. **Árbol Binario de Búsqueda (ABB):** Implementación orientada a objetos con control de duplicados y recorrido inorden iterativo para prevenir desbordamientos de recursión. Complejidad O(log N) en caso promedio, O(N) en peor caso.
3. **Árbol B+:** Estructura avanzada con orden configurable (por defecto 8), búsqueda binaria interna en nodos usando `bisect`, y punteros de hoja enlazados para consultas por rango optimizadas. Complejidad O(log N) garantizada.

## Archivos del Repositorio

| Archivo/Carpeta | Descripción |
| :--- | :--- |
| `arboles.ipynb` | Notebook principal con: generación de datasets, validación automática, 8 experimentos completos con análisis estadístico riguroso y generación de gráficas. |
| `estructuras.py` | Módulo Python con las tres estructuras de datos implementadas (ListaNat, ABB, ArbolBPlus) |
| `graficas/` | Carpeta conteniendo todas las gráficas comparativas de los experimentos (escalabilidad, impacto del orden de inserción, búsquedas por rango, sensibilidad al orden del B+, etc.). |
| `Informe-Lab-3.pdf` | Informe técnico detallado con metodología experimental, resultados estadísticos (media, desviación estándar, IC 95%, tratamiento de outliers), análisis de complejidad empírica y conclusiones. Generado a partir del Notebook omitiendo bloques de código para una mejor lectura. |

## Metodología Experimental

El estudio incluye **8 experimentos** diseñados para responder preguntas específicas sobre escalabilidad y comportamiento:

### Características del Benchmarking

* **Medición de alta precisión:** `time.perf_counter()` con resolución de nanosegundos
* **Minimización de ruido:** `gc.disable()` durante mediciones y calentamiento previo (100 búsquedas sin medir)
* **Rigor estadístico:** 10 repeticiones por experimento (5 en lotes masivos), reporte de media ± desviación estándar, mediana e Intervalo de Confianza del 95%
* **Tratamiento de outliers:** Criterio de Tukey (IQR) - reportados pero no eliminados para transparencia
* **Generación reproducible:** Dataset con semilla fija (SEED=42) usando Faker
* **Análisis de complejidad:** Regresión lineal en escala log-log para calcular exponentes empíricos

### Experimentos Realizados

1. **Impacto del orden de inserción:** Comparación ABB vs B+ con datos aleatorios vs. ordenados (demostración de degeneración del ABB)
2. **Escalabilidad de búsquedas:** Exitosas (M=5,000) con N variable [10, 50, 100, 500, 1K, 5K, 10K, 50K, 100K]
3. **Búsquedas fallidas:** Mismo diseño que Exp. 2 pero con IDs inexistentes
4. **Costo de construcción:** Tiempo de inserción masiva desde cero
5. **Efecto de M busquedas:** Tiempo total vs. número de búsquedas (N=50,000 fijo, M variable)
6. **Búsquedas por rango:** Ventaja del B+ con hojas enlazadas (rangos de 100 a 10,000 elementos)
7. **Listado ordenado:** Comparación de `listar_ordenado()` en las tres estructuras
8. **Inserción incremental:** Costo de insertar K=1,000 nuevos registros en estructuras ya pobladas
9. **Sensibilidad al orden del B+:** Impacto del parámetro de orden (4, 8, 16, 32, 64, 128) en altura y rendimiento

## Resultados Principales

### Validación de Complejidades Teóricas

* **Lista Nativa:** O(N) confirmado (exponente empírico = 1.01, R² = 0.989)
* **ABB:** O(log N) con datos aleatorios (exponente = 0.23, R² = 0.904)
* **B+:** O(log N) garantizado (exponente = 0.19, R² = 0.908)

### Hallazgos Críticos

* **Degeneración del ABB:** Con datos ordenados (N=20,000), la altura llega a 20,000 y el tiempo de búsqueda es **276x más lento** que con datos aleatorios
* **Punto de crossover:** Las diferencias se vuelven significativas a partir de **N ≥ 50** elementos
* **Superioridad del B+:**
  * Inmune al orden de inserción
  * Óptimo para consultas por rango (1.35x más rápido que ABB en rangos grandes)
  * Comportamiento predecible (búsquedas exitosas y fallidas tienen tiempos similares)
* **Relación altura-tiempo:** Correlación directa con R² ≈ 0.99

### Benchmark Típico (N=50,000, M=5,000 búsquedas)

* **Lista Nativa:** ~1.35 segundos (tiempo total)
* **Árbol ABB:** ~0.026 segundos (**52x más rápido** que Lista)
* **Árbol B+:** ~0.017 segundos (**79x más rápido** que Lista, **1.5x más rápido** que ABB)

## Instrucciones de Ejecución

1. Clonar el repositorio
2. Instalar dependencias: `pip install faker numpy scipy matplotlib jupyter`
3. Ejecutar el notebook: `jupyter notebook arboles.ipynb`
4. Para reproducir los experimentos completos, ejecutar todas las celdas secuencialmente (tiempo estimado: 15-20 minutos)
5. Las gráficas se generan automáticamente y se pueden exportar desde el notebook

## Notas aclaratorias y Declaración de Uso de IA

### Implementación

* **Árbol ABB:** Estructura desarrollada con asistencia de **GitHub Copilot** para la lógica base de inserción, búsqueda y recorrido.
* **Árbol B+:** Implementación adaptada y ajustada a partir de la referencia didáctica publicada en [Programiz](https://www.programiz.com/dsa/b-plus-tree). Se modificó para:
  * Soporte de claves enteras (IDs de estudiante)
  * Eliminación de agrupación de valores múltiples
  * Adición de métodos `buscar()`, `listar_ordenado()`, `buscar_rango()` y `altura()`
  * Optimización con búsqueda binaria interna (`bisect`)

### Experimentación y Análisis

* **Bloque de experimentación y generación de gráficas:** Estructurado y automatizado con asistencia de **Gemini 3.1 Pro** (Google).
* **Análisis estadístico:** Métodos sugeridos con IA (criterio de Tukey, regresión log-log, cálculo de IC 95%).
* **Redacción del informe:** Asistencia de IA para organización y claridad expositiva.

---

**Entorno de ejecución del estudio:**

* **Hardware:** Intel Core i5-13420H (13th Gen), 8 núcleos físicos, 15.6 GB RAM
* **Software:** Windows 11 (10.0.26200), Python 3.11.x, Faker 40.39.0, Matplotlib 3.11.2, NumPy 2.5.3, SciPy 1.18.1
* **Fecha de experimentación:** Octubre 2026
