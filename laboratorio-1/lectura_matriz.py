import time
import numpy as np

# FUNCIONES DE LECTURA Y MANIPULACIÓN EFICIENTE

def obtener_tamano_archivo(archivo, n_filas, bytes_por_fila):
    """
    Calcula el peso total del archivo mapeado en memoria en Megabytes (MB).

    Args:
        archivo (str): Ruta del archivo binario en disco.
        n_filas (int): Número total de filas de la matriz.
        bytes_por_fila (int): Cantidad de bytes que ocupa una fila (N // 8).

    Returns:
        float: Tamaño del archivo en MB.
    """
    mm = np.memmap(archivo, dtype=np.uint8, mode="r", shape=(n_filas, bytes_por_fila))
    tamano_mb = mm.nbytes / (1024 * 1024)
    del mm
    return tamano_mb

def obtener_metadata(archivo, n_filas, bytes_por_fila):
    """
    Recupera y calcula información estructural relevante sobre el archivo mapeado en disco.

    Args:
        archivo (str): Ruta del archivo binario.
        n_filas (int): Número total de filas.
        bytes_por_fila (int): Bytes por fila.

    Returns:
        dict: Diccionario con métricas de la matriz (dimensiones, espacio y empaquetado).
    """
    mm = np.memmap(archivo, dtype=np.uint8, mode="r", shape=(n_filas, bytes_por_fila))
    bytes_totales = mm.nbytes
    tamano_mb = bytes_totales / (1024 * 1024)
    tamano_gb = tamano_mb / 1024
    del mm

    return {
        "dimensiones_logicas": f"{n_filas:,} x {n_filas:,} bits",
        "dimensiones_fisicas": f"{n_filas:,} x {bytes_por_fila:,} bytes",
        "bytes_totales": f"{bytes_totales:,} bytes",
        "peso_mb": round(tamano_mb, 2),
        "peso_gb": round(tamano_gb, 2),
        "empaquetado": "8 bits por byte (uint8)"
    }

def mostrar_fila(archivo, n_filas, bytes_por_fila, fila, limite_cols=10):
    """
    Extrae y desempaqueta los bits pertenecientes a una fila completa.

    Args:
        archivo (str): Ruta del archivo binario.
        n_filas (int): Número total de filas.
        bytes_por_fila (int): Bytes por fila.
        fila (int): Índice de la fila a consultar.
        limite_cols (int, optional): Muestra de bits iniciales para visualizar en consola. 
                                     Si es None, retorna el arreglo completo de 100,000 bits.

    Returns:
        np.ndarray: Arreglo de bits (0 y 1) de la fila seleccionada.
    """
    mm = np.memmap(archivo, dtype=np.uint8, mode="r", shape=(n_filas, bytes_por_fila))
    fila_bytes = mm[fila, :]
    fila_bits = np.unpackbits(fila_bytes)
    del mm

    if limite_cols is not None:
        return fila_bits[:limite_cols]
    return fila_bits

def consultar_celda(archivo, n_filas, bytes_por_fila, fila, columna):
    """
    Consulta mediante acceso aleatorio el valor exacto de un bit (0 o 1).

    Args:
        archivo (str): Ruta del archivo binario.
        n_filas (int): Número total de filas.
        bytes_por_fila (int): Bytes por fila.
        fila (int): Índice de la fila objetivo.
        columna (int): Índice de la columna objetivo (bit).

    Returns:
        int: Valor del bit leído (0 o 1).
    """
    mm = np.memmap(archivo, dtype=np.uint8, mode="r", shape=(n_filas, bytes_por_fila))
    col_byte = columna // 8
    offset_bit = columna % 8
    
    byte_leido = mm[fila, col_byte]
    bit_resultado = np.unpackbits(byte_leido)[offset_bit]
    del mm
    return bit_resultado

def modificar_celda(archivo, n_filas, bytes_por_fila, fila, columna, nuevo_valor):
    """
    Sobrescribe un único bit en el disco duro sin alterar el resto de los bits 
    del byte contenedor. Utiliza mapeo en modo lectura/escritura ('r+').

    Args:
        archivo (str): Ruta del archivo binario.
        n_filas (int): Número total de filas.
        bytes_por_fila (int): Bytes por fila.
        fila (int): Índice de la fila.
        columna (int): Índice de la columna (bit).
        nuevo_valor (int): Nuevo valor a asignar (0 o 1).
    """
    mm = np.memmap(archivo, dtype=np.uint8, mode="r+", shape=(n_filas, bytes_por_fila))
    
    col_byte = columna // 8
    offset_bit = columna % 8
    
    byte_actual = np.array([mm[fila, col_byte]], dtype=np.uint8)
    bits = np.unpackbits(byte_actual)
    
    bits[offset_bit] = nuevo_valor
    mm[fila, col_byte] = np.packbits(bits)[0]
    
    mm.flush()
    del mm

def extraer_submatriz(archivo, n_filas, bytes_por_fila, filas_rango, cols_rango):
    """
    Extrae y desempaqueta un sub-bloque de la matriz para su visualización 
    y análisis rápido sin cargar todo el archivo a la RAM.

    Args:
        archivo (str): Ruta del archivo binario.
        n_filas (int): Número total de filas.
        bytes_por_fila (int): Bytes por fila.
        filas_rango (tuple): Rango de filas en formato (inicio, fin).
        cols_rango (tuple): Rango de columnas en formato (inicio, fin).

    Returns:
        np.ndarray: Sub-matriz de bits (0 y 1).
    """
    mm = np.memmap(archivo, dtype=np.uint8, mode="r", shape=(n_filas, bytes_por_fila))
    
    f_inicio, f_fin = filas_rango
    c_inicio, c_fin = cols_rango
    
    byte_inicio = c_inicio // 8
    byte_fin = (c_fin // 8) + 1
    
    bloque_bytes = mm[f_inicio:f_fin, byte_inicio:byte_fin]
    bloque_bits = np.unpackbits(bloque_bytes, axis=1)
    
    offset_c = c_inicio % 8
    ancho_c = c_fin - c_inicio
    vista_final = bloque_bits[:, offset_c : offset_c + ancho_c]
    
    del mm
    return vista_final

if __name__ == "__main__":
    RUTA_ARCHIVO = "../matriz_disco.bin"
    N = 100_000
    BYTES_FILA = N // 8

    print("=" * 65)
    print(" AUDITORÍA COMPLETA Y MANIPULACIÓN DE MATRIZ EN DISCO")
    print("=" * 65)

    # 1. Obtener Metadata
    print("\n[1] METADATA DEL ARCHIVO:")
    metadata = obtener_metadata(RUTA_ARCHIVO, N, BYTES_FILA)
    for clave, valor in metadata.items():
        print(f"  • {clave}: {valor}")

    # 2. Consultar Celda
    f_obj, c_obj = 50_000, 80_005
    val_orig = consultar_celda(RUTA_ARCHIVO, N, BYTES_FILA, f_obj, c_obj)
    print(f"\n[2] CONSULTA PUNTUAL: Celda [{f_obj:,}, {c_obj:,}] = {val_orig}")

    # 3. Modificar Celda
    nuevo_v = 1 if val_orig == 0 else 0
    modificar_celda(RUTA_ARCHIVO, N, BYTES_FILA, f_obj, c_obj, nuevo_v)
    val_mod = consultar_celda(RUTA_ARCHIVO, N, BYTES_FILA, f_obj, c_obj)
    print(f"[3] MANIPULACIÓN: Celda [{f_obj:,}, {c_obj:,}] actualizada a = {val_mod}")

    # 4. Mostrar Fila
    fila_demo = 0
    bits_fila = mostrar_fila(RUTA_ARCHIVO, N, BYTES_FILA, fila_demo, limite_cols=100_000)
    print(f"\n[4] MOSTRAR FILA {fila_demo} (Fila completa de 100,000 bits): ")
    print(f"  {bits_fila}")
    print(f"Tamaño de la fila: {len(bits_fila)}")

    # 5. Mostrar Bloque (Sub-matriz)
    r_f, r_c = (0, 5), (0, 5)
    bloque = extraer_submatriz(RUTA_ARCHIVO, N, BYTES_FILA, r_f, r_c)
    print(f"\n[5] MOSTRAR BLOQUE ({r_f[0]}:{r_f[1]} filas x {r_c[0]}:{r_c[1]} cols):")
    print(bloque)
    print("=" * 65)