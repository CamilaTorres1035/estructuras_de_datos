"""
    Optimización de la búsqueda de la clave que genera el hash objetivo
    
    Razón: 
    Un caso extremo como 99999999 clave en la implementación original (bucle secuencial y conversión a str) demora ~5 minutos, con la versión optimizada demora ~18 segundos
    (probado en una CPU de 12 núcleos)
    (hash de prueba (99999999): 3f08d8fadb4b67fb056623565edbbc2c788091d78fd24cbc473fce3043ce3473)
    
    Implementación:
    - Microoptimización formateando directamente a bytes (b"%08d") eliminando conversión a str y uso de .encode
    - Usando multiprocessing se obtiene la cantidad de núcleos del procesador 
    - Se divide el total de combinaciones posibles en la cantidad de núcleos para definir el tamaño del chunk a evaluar por cada uno de los núcleos
    - Usando multiprocessing.Pool se le asigna una tarea (ejecutar la función de búsqueda en un rango específico) a cada núcleo, cada uno analiza el rango completo que le corresponde
    - Se mide el tiempo con time para realizar la comparación con la búsqueda pura
    
    Notas adicionales:
    - El hash objetivo debe estar completamente en minúsculas.
    - Aunque un núcleo encuentre la clave antes, 'starmap' esperará a que todos los procesos terminen su rango antes de devolver el control.
"""

import hashlib
import multiprocessing
import time

def buscar_en_rango(inicio, fin, hash_objetivo):
    """
    Busca el hash objetivo dentro de un rango numérico específico.

    Args:
        inicio (int): Límite inferior del rango a evaluar.
        fin (int): Límite superior del rango a evaluar.
        hash_objetivo (str): Hash SHA-256 en formato hexadecimal minúsculo.

    Returns:
        str | None: La clave de 8 dígitos encontrada o None si no existe en el rango.
    """
    for i in range(inicio, fin):
        cadena_bytes = b"%08d" % i
        if hashlib.sha256(cadena_bytes).hexdigest() == hash_objetivo:
            return cadena_bytes.decode()
    return None

if __name__ == '__main__':
    print("!Este programa solo encuentra claves de 8 dígitos¡")
    print("Ingrese el hash objetivo (en SHA-256 en cadena hexadecimal): ")
    hash_objetivo = input()
    
    # Obtener la cantidad de núcleos del procesador
    nucleos = multiprocessing.cpu_count()
    total_combinaciones = 100_000_000
    # Definir tamaño del chunk de combinaciones a evaluar
    tamaño_bloque = total_combinaciones // nucleos
    
    # Crear tuplas de los rangos junto al hash objetivo
    tareas = []
    for i in range(nucleos):
        inicio = i * tamaño_bloque
        # Asegurarse de que el último bloque llegue hasta el final
        fin = (i + 1) * tamaño_bloque if i != nucleos - 1 else total_combinaciones
        tareas.append((inicio, fin, hash_objetivo))

    print(f"Iniciando búsqueda usando {nucleos} núcleos...")
    
    # INICIO DEL CRONÓMETRO
    tiempo_inicio = time.perf_counter()

    # Ejecutar en paralelo
    with multiprocessing.Pool(nucleos) as pool:
        # starmap permite pasar múltiples argumentos a la función
        resultados = pool.starmap(buscar_en_rango, tareas)
        
        # Filtrar el resultado exitoso
        for res in resultados:
            if res is not None:
                print(f"\n¡Clave encontrada!: {res}")
                break
        else:
            print("\nClave no encontrada en el rango.")
            
    # FIN DEL CRONÓMETRO 
    tiempo_fin = time.perf_counter()
    tiempo_total = tiempo_fin - tiempo_inicio
    
    print(f"Tiempo de ejecución: {tiempo_total:.2f} segundos")