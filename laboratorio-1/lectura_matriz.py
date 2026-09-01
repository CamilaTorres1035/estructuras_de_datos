import time
import numpy as np

# FUNCIONES DE LECTURA Y MANIPULACIÓN EFICIENTE

def obtener_tamano_archivo(archivo, n_filas, bytes_por_fila):
    mm = np.memmap(archivo, dtype=np.uint8, mode="r", shape=(n_filas, bytes_por_fila))
    tamano_mb = mm.nbytes / (1024 * 1024)
    del mm
    return tamano_mb

def consultar_celda(archivo, n_filas, bytes_por_fila, fila, columna):
    mm = np.memmap(archivo, dtype=np.uint8, mode="r", shape=(n_filas, bytes_por_fila))
    col_byte = columna // 8
    offset_bit = columna % 8
    
    byte_leido = mm[fila, col_byte]
    bit_resultado = np.unpackbits(byte_leido)[offset_bit]
    del mm
    return bit_resultado

def modificar_celda(archivo, n_filas, bytes_por_fila, fila, columna, nuevo_valor):
    """Sobrescribe un único bit en el disco duro sin alterar el resto del byte (Manipulación)."""
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
    
    print("--- INICIANDO AUDITORÍA Y MANIPULACIÓN ---")
    print(f"Peso del archivo: {obtener_tamano_archivo(RUTA_ARCHIVO, N, BYTES_FILA):.2f} MB")
    
    # Prueba de lectura
    f_obj, c_obj = 50_000, 80_005
    val_original = consultar_celda(RUTA_ARCHIVO, N, BYTES_FILA, f_obj, c_obj)
    print(f"Valor original en [{f_obj}, {c_obj}]: {val_original}")
    
    # Prueba de manipulación (cambiar por su inverso)
    nuevo_val = 1 if val_original == 0 else 0
    modificar_celda(RUTA_ARCHIVO, N, BYTES_FILA, f_obj, c_obj, nuevo_val)
    val_modificado = consultar_celda(RUTA_ARCHIVO, N, BYTES_FILA, f_obj, c_obj)
    print(f"Valor tras modificación en [{f_obj}, {c_obj}]: {val_modificado}")