# Laboratorio 1: Matriz de 100.000 x 100.000 en el disco duro

**Estudiante:** Maria Camila Torres Chica

## Requisitos Generales del Entorno

* **Lenguaje:** Python 3.10 o superior.
* **Dependencias principales:** `numpy`

## Descripción

En este laboratorio se abordó el reto de crear, almacenar y manipular una matriz de gran escala ($100{,}000 \times 100{,}000$ elementos) de forma optimizada y minimizando el impacto en memoria RAM.

### Problemas Resueltos

1. **Consumo excesivo de RAM:** Se evita cargar la matriz completa en la memoria principal utilizando archivos mapeados en memoria (`np.memmap`) y procesamiento por bloques (*chunks*).

2. **Escritura lenta a disco:** Se reducen las llamadas del sistema mediante el volcado en bloques dinámicos de $5{,}000$ filas, permitiendo que el SO gestione el caché de páginas de forma eficiente.

3. **Optimización de datos (Bit-Packing):** En lugar de almacenar cada elemento como un entero o booleano de 1 byte, se empaquetan 8 bits en un único byte (`np.uint8`), reduciendo el tamaño total del archivo de 10 GB a aproximadamente **1.16 GB** ($1,192.09 \text{ MB}$).

## Archivos del Repositorio

| Archivo | Descripción |
| :--- | :--- |
| `creacion_matriz.py` | Script que ejecuta la generación iterativa de la matriz y su almacenamiento empaquetado en disco mediante mapeo de memoria (`np.memmap`). |
| `lectura_matriz.py` | Módulo que documenta e implementa funciones de metadatos, visualización de filas completas, acceso aleatorio a celdas individuales, modificación de bits en disco y extracción de sub-matrices (bloques). |
| `matriz_disco.bin` | Archivo binario que almacena la matriz empaquetada (excluido en el `.gitignore` por su tamaño de $\approx 1.16 \text{ GB}$). |

## Verificación y Manipulación de la Matriz

El repositorio incluye métodos ejecutables en `lectura_matriz.py` que permiten auditar y alterar los datos sin saturar la memoria RAM:

1. **Obtener Metadata (`obtener_metadata` y `obtener_tamano_archivo`):**
   Recupera las métricas estructurales del archivo mapeado (dimensiones lógicas y físicas en bytes, peso total en MB/GB y el factor de empaquetado de 8 bits por byte).

2. **Mostrar Fila (`mostrar_fila`):**
   Extrae y desempaqueta los bits pertenecientes a una fila completa, permitiendo visualizar una muestra inicial o retornar el arreglo completo de $100{,}000$ bits de manera eficiente.

3. **Acceso Aleatorio a Bits Específicos (`consultar_celda`):**
   Calcula de forma matemática el byte correspondiente ($\text{columna} // 8$) y extrae el bit exacto usando `np.unpackbits()`, permitiendo consultar cualquier celda de la matriz de $100{,}000 \times 100{,}000$ de manera instantánea.

4. **Manipulación y Actualización de Celdas (`modificar_celda`):**
   Abre el archivo en modo lectura/escritura (`r+`) para sobrescribir un bit específico directamente en el disco duro. Lee el byte contenedor, aísla el bit mediante `np.unpackbits()`, lo actualiza y lo reempaqueta con `np.packbits()` sin alterar los otros 7 bits vecinos, aplicando `mm.flush()` para sincronizar los cambios físicamente.

5. **Inspección de Sub-bloques / Mostrar Bloque (`extraer_submatriz`):**
   Permite extraer y desempaquetar porciones específicas parametrizadas por un rango de filas y columnas (ej. vistas de $5 \times 5$) para auditar visualmente los valores lógicos almacenados.
