import os
import mmap
import struct
import hashlib

# Configuraciones base de nuestra base de datos
HEADER_SIZE = 12
BUCKET_SIZE = 4096
INITIAL_BUCKETS = 4
FILE_NAME = "linear_hash_db.bin"

def init_database():
    # Calculamos el tamaño total: 12 bytes (encabezado) + 16384 bytes (4 buckets)
    total_size = HEADER_SIZE + (INITIAL_BUCKETS * BUCKET_SIZE)
    
    # Creamos el archivo binario y lo llenamos de ceros (reservamos el espacio)
    with open(FILE_NAME, "wb") as f:
        f.write(b'\x00' * total_size)
        
    # Abrimos el archivo mapeado en memoria para escribir los metadatos
    with open(FILE_NAME, "r+b") as f:
        # Mapeamos todo el archivo a memoria
        mm = mmap.mmap(f.fileno(), 0)
        
        # Variables iniciales del Hashing Lineal
        N = INITIAL_BUCKETS
        L = 0 # Nivel actual
        s = 0 # Split Pointer
        
        # Empaquetamos N, L y s a nivel de bits
        # '<III' = Little-endian, 3 enteros sin signo (4 bytes cada uno = 12 bytes total)
        mm[0:HEADER_SIZE] = struct.pack('<III', N, L, s)
        
        # Forzamos la escritura física en el disco duro y cerramos
        mm.flush()
        mm.close()
        
    print(f"[*] Base de datos inicializada en '{FILE_NAME}'")
    print(f"[*] Tamaño reservado: {total_size} bytes (Encabezado + {INITIAL_BUCKETS} Buckets libres)")

def read_header(mm):
    mm.seek(0)
    header_data = mm.read(HEADER_SIZE)
    N, L, s = struct.unpack('<III', header_data)
    return N, L, s

def get_stable_hash(key_string):
    # Generamos un hash estable simulando el efecto avalancha
    hash_bytes = hashlib.md5(key_string.encode('utf-8')).digest()
    # Convertimos los primeros 4 bytes en un entero sin signo
    return struct.unpack('<I', hash_bytes[:4])[0]

def get_bucket_offset(key_string, N, L, s):
    hash_int = get_stable_hash(key_string)
    # Calculamos el bucket con el nivel actual L
    modulo_L = N * (2 ** L)
    bucket = hash_int % modulo_L
    
    # Si el bucket ya fue dividido por el split pointer, recalculamos con L+1
    if bucket < s:
        modulo_L1 = N * (2 ** (L + 1))
        bucket = hash_int % modulo_L1
        
    # Calculamos el offset exacto en bytes dentro del archivo
    offset = HEADER_SIZE + (bucket * BUCKET_SIZE)
    return bucket, offset

# Definimos las longitudes binarias de un registro
MAX_RECORDS = 2  # Capacidad de 2 por bucket para forzar el desbordamiento rápido
KEY_SIZE = 16
VAL_SIZE = 32
RECORD_SIZE = KEY_SIZE + VAL_SIZE      # 48 bytes por registro
BUCKET_HEADER_SIZE = 8                 # 4 bytes (contador) + 4 bytes (overflow_ptr)

def put(mm, key_string, value_string, N, L, s):
    # Calculamos en qué byte del disco cae esta clave
    bucket_index, offset = get_bucket_offset(key_string, N, L, s)
    
    # Leemos el encabezado de ese bucket específico
    mm.seek(offset)
    bucket_header = mm.read(BUCKET_HEADER_SIZE)
    count, overflow_ptr = struct.unpack('<II', bucket_header)
    
    # Verificamos si hay espacio en la página
    if count < MAX_RECORDS:
        # Calculamos el byte exacto donde empieza nuestro espacio libre:
        # Inicio del bucket + 8 bytes de encabezado + espacio ocupado por registros anteriores
        record_offset = offset + BUCKET_HEADER_SIZE + (count * RECORD_SIZE)
        
        # Empaquetamos los strings forzando el tamaño exacto (padding)
        key_bytes = key_string.ljust(KEY_SIZE).encode('utf-8')[:KEY_SIZE]
        val_bytes = value_string.ljust(VAL_SIZE).encode('utf-8')[:VAL_SIZE]
        
        # Escribimos el par clave-valor directamente en el disco
        mm.seek(record_offset)
        mm.write(key_bytes + val_bytes)
        
        # Actualizamos y guardamos el contador del bucket
        count += 1
        mm.seek(offset)
        mm.write(struct.pack('<II', count, overflow_ptr))
        
        print(f"[*] Guardado: '{key_string.strip()}' -> Bucket {bucket_index}")
        
    else:
        # COLISIÓN Y DESBORDAMIENTO
        print(f"[!] Overflow en Bucket {bucket_index} insertando '{key_string}'.")
        print(f"[!] Es hora de crear una página de overflow y avanzar el split pointer.")

def trigger_split(mm, N, L, s):
    print(f"\n[SPLIT] Iniciando división. Split Pointer (s) apunta al Bucket {s}")
    
    # Identificar a los protagonistas
    bucket_original = s
    bucket_nuevo = s + (N * (2 ** L))
    
    offset_original = HEADER_SIZE + (bucket_original * BUCKET_SIZE)
    offset_nuevo = HEADER_SIZE + (bucket_nuevo * BUCKET_SIZE)
    
    # (Nota del sistema: En un entorno real de producción, aquí extenderías 
    # el tamaño del archivo físico y redimensionarías el mmap antes de continuar).
    
    # Leer TODOS los registros del bucket original
    mm.seek(offset_original)
    count, overflow_ptr = struct.unpack('<II', mm.read(BUCKET_HEADER_SIZE))
    
    registros_extraidos = []
    for i in range(count):
        mm.seek(offset_original + BUCKET_HEADER_SIZE + (i * RECORD_SIZE))
        registro_crudo = mm.read(RECORD_SIZE)
        registros_extraidos.append(registro_crudo)
        
    # Limpiar los buckets (formatear encabezados a 0 registros)
    mm.seek(offset_original)
    mm.write(struct.pack('<II', 0, overflow_ptr)) # Conservamos el overflow si lo hubiera
    
    mm.seek(offset_nuevo)
    mm.write(struct.pack('<II', 0, 0)) # El nuevo nace limpio
    
    # Redistribuir (Rehashing) evaluando con L + 1
    modulo_L1 = N * (2 ** (L + 1))
    
    for registro in registros_extraidos:
        # Extraer y limpiar la clave de los bytes crudos
        key_bytes = registro[:KEY_SIZE]
        key_string = key_bytes.decode('utf-8').strip('\x00').strip()
        
        # La nueva prueba de fuego matemática
        hash_int = get_stable_hash(key_string)
        nuevo_destino = hash_int % modulo_L1
        
        # Dependiendo del resultado, lo re-insertamos físicamente
        if nuevo_destino == bucket_original:
            destino_offset = offset_original
            print(f"   -> '{key_string}' SE QUEDA en el Bucket {bucket_original}")
        else:
            destino_offset = offset_nuevo
            print(f"   -> '{key_string}' SE MUDA al Bucket {bucket_nuevo}")
            
        # Lógica rápida de escritura (similar a put)
        mm.seek(destino_offset)
        nuevo_count, _ = struct.unpack('<II', mm.read(BUCKET_HEADER_SIZE))
        
        mm.seek(destino_offset + BUCKET_HEADER_SIZE + (nuevo_count * RECORD_SIZE))
        mm.write(registro)
        
        # Actualizar el contador del bucket receptor
        mm.seek(destino_offset)
        mm.write(struct.pack('<II', nuevo_count + 1, 0))

    # Avanzar el Split Pointer
    s += 1
    
    # Control de Cambio de Nivel
    if s == N * (2 ** L):
        print(f"[NIVEL COMPLETADO] Todos los buckets base se dividieron. Subiendo a Nivel {L + 1}")
        s = 0
        L += 1
        
    # Persistir el nuevo estado de las variables en el encabezado del archivo
    mm.seek(0)
    mm.write(struct.pack('<III', N, L, s))
    
    return N, L, s

def expand_file_for_new_bucket():
    # Cierra el mmap actual temporalmente, agranda el archivo en 4KB y lo vuelve a mapear
    current_size = os.path.getsize(FILE_NAME)
    new_size = current_size + BUCKET_SIZE
    
    with open(FILE_NAME, "r+b") as f:
        f.seek(new_size - 1)
        f.write(b'\x00') # Escribe un byte al final para forzar el crecimiento del archivo
        
    print(f"[DISCO] Archivo expandido a {new_size} bytes.")

# simulación
if __name__ == "__main__":
    init_database()
    
    # Abrimos la conexión al motor
    with open(FILE_NAME, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)
        
        # Leemos el estado inicial
        N, L, s = read_header(mm)
        
        # Lote de datos de prueba (textos con diferentes longitudes)
        datos_prueba = [
            ("isbn_001", "Un paseo por la vida"),
            ("isbn_002", "La perra"),
            ("isbn_003", "Lo que no tiene nombre"),
            ("isbn_004", "Yerba Buena"),
            ("isbn_005", "The Power"),
            ("isbn_006", "La biblioteca de la medianoche"),
            ("isbn_007", "Cada seis meses"),
            ("isbn_008", "Los siete maridos de Evelyn Hugo"), # Este debería detonar el overflow
            ("isbn_009", "La oscuridad de los colores")
        ]
        
        print("\n--- INICIANDO INSERCIONES ---")
        for key, value in datos_prueba:
            # Intentamos insertar
            bucket_index, offset = get_bucket_offset(key, N, L, s)
            
            # Revisamos si el bucket está lleno antes de llamar a put()
            mm.seek(offset)
            count, _ = struct.unpack('<II', mm.read(BUCKET_HEADER_SIZE))
            
            if count >= MAX_RECORDS:
                print(f"\n[!] Overflow detectado intentando insertar '{key}' en Bucket {bucket_index}")
                
                # Expandimos el disco físicamente
                mm.close()
                expand_file_for_new_bucket()
                
                # Volvemos a mapear el archivo ahora que es más grande
                mm = mmap.mmap(f.fileno(), 0)
                
                # Disparamos la división matemática
                N, L, s = trigger_split(mm, N, L, s)
                
            # Ahora sí, guardamos el dato de forma segura
            put(mm, key, value, N, L, s)
            
        mm.close()
        print("\n--- SIMULACIÓN FINALIZADA ---")