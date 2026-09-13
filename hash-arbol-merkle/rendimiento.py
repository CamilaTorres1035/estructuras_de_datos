import hashlib
import multiprocessing
import time

# --- VERSIÓN ORIGINAL (Mononúcleo + Conversiones lentas) ---
def buscar_original(total_combinaciones, hash_objetivo):
    for i in range(total_combinaciones):
        cadena = str(i).zfill(8)
        if hashlib.sha256(cadena.encode()).hexdigest() == hash_objetivo:
            return cadena
    return None

# --- VERSIÓN OPTIMIZADA (Multiproceso + Bytes directos) ---
def buscar_en_rango_optimizado(inicio, fin, hash_objetivo):
    for i in range(inicio, fin):
        cadena_bytes = b"%08d" % i
        if hashlib.sha256(cadena_bytes).hexdigest() == hash_objetivo:
            return cadena_bytes.decode()
    return None

def buscar_optimizado(total_combinaciones, hash_objetivo):
    nucleos = multiprocessing.cpu_count()
    tamaño_bloque = total_combinaciones // nucleos
    
    tareas = []
    for i in range(nucleos):
        inicio = i * tamaño_bloque
        fin = (i + 1) * tamaño_bloque if i != nucleos - 1 else total_combinaciones
        tareas.append((inicio, fin, hash_objetivo))

    with multiprocessing.Pool(nucleos) as pool:
        resultados = pool.starmap(buscar_en_rango_optimizado, tareas)
        for res in resultados:
            if res is not None:
                return res
    return None

# --- UTILIDAD PARA FORMATEAR HASHES POR SEGUNDO ---
def formatear_hps(hps):
    if hps >= 1_000_000:
        return f"{hps / 1_000_000:.2f} MH/s"
    elif hps >= 1_000:
        return f"{hps / 1_000:.2f} kH/s"
    return f"{hps:.2f} H/s"

# --- TEST COMPARATIVO DE RENDIMIENTO ---
def probar_tiempos():
    # Rangos de combinaciones a evaluar
    casos_de_prueba = [100_000, 500_000, 1_000_000, 2_000_000, 10_000_000]
    # Número de iteraciones para evaluar cada caso
    iteraciones = 2 

    nucleos = multiprocessing.cpu_count()
    print(f"Iniciando Benchmark Comparativo en Peor Caso ({nucleos} núcleos)...")
    print("=" * 82)
    print(f"{'Combinaciones':<13} | {'Tiempo Orig.':<12} | {'Tiempo Opt.':<12} | {'H/s (Opt.)':<12} | {'Aceleración':<10}")
    print("=" * 82)

    for n in casos_de_prueba:
        # Generar hash del último número posible del rango
        clave_peor_caso = b"%08d" % (n - 1)
        hash_prueba = hashlib.sha256(clave_peor_caso).hexdigest()
        
        # 1. Medir Versión Original
        t_orig_acumulado = 0
        for _ in range(iteraciones):
            inicio = time.perf_counter()
            buscar_original(n, hash_prueba)
            t_orig_acumulado += (time.perf_counter() - inicio)
        t_orig = t_orig_acumulado / iteraciones
        
        # 2. Medir Versión Optimizada
        t_opt_acumulado = 0
        for _ in range(iteraciones):
            inicio = time.perf_counter()
            buscar_optimizado(n, hash_prueba)
            t_opt_acumulado += (time.perf_counter() - inicio)
        t_opt = t_opt_acumulado / iteraciones
        
        # 3. Métricas
        hps_optimizado = n / t_opt if t_opt > 0 else 0
        aceleracion = t_orig / t_opt if t_opt > 0 else 0
        
        # Mostrar resultados formateados
        print(f"{n:<13,} | {t_orig:<11.3f}s | {t_opt:<11.3f}s | {formatear_hps(hps_optimizado):<12} | {aceleracion:.1f}x más rápido")

if __name__ == "__main__":
    probar_tiempos()