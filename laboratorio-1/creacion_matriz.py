import time
import numpy as np

# Configuración inicial
N = 100_000
BYTES_FILA = N // 8  # Empaquetado de 8 bits por byte
CHUNK_SIZE = 5_000   # Bloque ajustado para minimizar llamadas I/O
ARCHIVO = "../matriz_disco.bin"

# ESCRITURA EN DISCO (Optimización de Memoria e I/O)

inicio = time.time()

# Crear archivo binario mapeado en memoria (modo w+)
mm_write = np.memmap(ARCHIVO, dtype=np.uint8, mode="w+", shape=(N, BYTES_FILA))
rng = np.random.default_rng(42)

for i in range(0, N, CHUNK_SIZE):
    limite = min(CHUNK_SIZE, N - i)
    # Generación y asignación directa a la vista mapeada
    mm_write[i : i + limite] = rng.integers(0, 256, size=(limite, BYTES_FILA), dtype=np.uint8)
    
    if i % 20_000 == 0:
        print(f"Progreso de escritura: {i} de {N} filas completadas...")

# Forzar escritura final y liberar recurso
mm_write.flush()
del mm_write

fin = time.time()
print(f"Matriz guardada en disco en {fin - inicio:.2f} segundos.\n")