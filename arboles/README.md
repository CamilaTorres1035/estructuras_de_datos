# Sistema de Búsqueda y Organización: Árboles ABB y B+

## Requisitos Generales del Entorno

* **Lenguaje:** Python 3.10 o superior.
* **Dependencias principales:** Librería `Faker` para la generación de datos, Módulos estándar de Python (`random`, `bisect`, `time`, `math`) y entorno Jupyter Notebook (`jupyter` / `notebook`).

## Descripción

Este módulo resuelve el problema de gestionar una base de datos en memoria de 10,000 estudiantes, permitiendo búsquedas por ID, inserciones y listados ordenados. El objetivo principal es comparar la eficiencia computacional de diferentes estructuras de datos frente a un volumen considerable de información.

### Estructuras Implementadas

1. **Lista Nativa:** Búsqueda secuencial estándar.
2. **Árbol Binario de Búsqueda (ABB):** Implementación orientada a objetos con control de duplicados y un método de listado ordenado (`listar_ordenado`) basado en recorrido inorden iterativo mediante pilas para prevenir desbordamientos de recursión.
3. **Árbol B+:** Estructura avanzada ideal para bases de datos. Se implementó con orden 8 y se integró el módulo `bisect` de Python (`bisect_left`, `bisect_right`) para reemplazar la iteración lineal dentro de los nodos por búsqueda binaria, reduciendo drásticamente la complejidad algorítmica.

## Archivos del Repositorio

| Archivo | Descripción |
| :--- | :--- |
| `arboles.ipynb` | Notebook interactivo que contiene la generación del dataset (con `Faker`), las tres estructuras de datos, las pruebas manuales de validación y un benchmark automatizado de rendimiento. |

## Benchmark de Rendimiento

El sistema incluye una celda de pruebas que ejecuta lotes de 500 búsquedas promediadas a lo largo de 50 repeticiones. Los resultados típicos demuestran la superioridad del Árbol B+:

* **Lista Nativa:** ~0.097 segundos por lote.
* **Árbol ABB:** ~0.0009 segundos por lote.
* **Árbol B+:** ~0.0007 segundos por lote.

## Notas aclaratorias

Para la construcción de este módulo se utilizaron las siguientes herramientas y referencias:

* **Árbol ABB:** Implementación base co-generada con asistencia de GitHub Copilot.
* **Árbol B+:** Estructura adaptada y ajustada a partir de la implementación didáctica publicada en [Programiz](https://www.programiz.com/dsa/b-plus-tree).
* **Pruebas de Rendimiento:** El bloque comparativo y la lógica de muestreo para el benchmark fueron estructurados con asistencia de Gemini 3.1 Pro.
