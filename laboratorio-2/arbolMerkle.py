import os
import json
import hashlib

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

class MerkelTree:
    def __init__(self, transacciones: list):
        """
        Constructor que inicializa el árbol como una matriz bidimensional inmutable
        que funciona bajo el concepto de pila.
        Detecta automáticamente si los datos son texto plano o diccionarios complejos.
        """
        if not transacciones:
            self.matriz = ((),)
            self.transacciones = ()
            return
        
        self.transacciones = tuple(transacciones)
        
        hojas = []
        for tx in transacciones:
            # Si es un diccionario/objeto complejo
            if isinstance(tx, dict):
                serializacion = json.dumps(tx, sort_keys=True)
                hojas.append(sha256(serializacion))
            # Si ya es un texto plano (string)
            else:
                hojas.append(sha256(str(tx)))
            
        self.matriz = [tuple(hojas)]
        
        # Construimos los siguientes niveles hacia arriba
        while len(self.matriz[-1]) > 1:
            capa_anterior = list(self.matriz[-1])
            
            # Si el nivel es impar, duplicamos el último elemento
            if len(capa_anterior) % 2 != 0:
                capa_anterior.append(capa_anterior[-1])
               
            siguiente_capa = []
            for i in range(0, len(capa_anterior), 2):
                combinacion = capa_anterior[i] + capa_anterior[i + 1]
                siguiente_capa.append(sha256(combinacion))
            
            self.matriz.append(tuple(siguiente_capa))
        
        self.matriz = tuple(self.matriz)
    
    def get_root(self) -> str:
        """Devuelve el hash raíz del árbol (el tope de la pila)."""
        return self.matriz[-1][0] if self.matriz else ""
    
    def get_proof(self, indice: int) -> list:
        """Genera los pasos de la prueba (Merkle Proof) para una transacción."""
        if indice < 0 or indice >= len(self.transacciones):
            return []
        
        prueba = []
        indice_actual = indice
        
        for capa in self.matriz[:-1]:
            es_impar = indice_actual % 2 == 1
            indice_pareja = indice_actual - 1 if es_impar else min(indice_actual + 1, len(capa) - 1)
            
            prueba.append({
                "posicion": "left" if es_impar else "right",
                "hash": capa[indice_pareja]
            })
            indice_actual //= 2
            
        return prueba
    
    def generar_reporte_texto(self) -> str:
        """Genera una cadena de texto con la estructura jerárquica del árbol."""
        root = self.get_root()
        hojas = self.matriz[0]
        lineas = []
        lineas.append(f"MERKLE ROOT FINAL:\n{root}\n")
        lineas.append("[RAÍZ]")
        lineas.append(f" |-- {root[:8]}... (HASH: {root})")
        
        if len(self.matriz) > 2:
            lineas.append("\n[NODOS INTERMEDIOS]")
            for i in range(len(self.matriz) - 2, 0, -1):
                for idx, h in enumerate(self.matriz[i]):
                    lineas.append(f" +-- H{i}{idx+1}: {h[:8]}...")
        
        lineas.append("\n[HOJAS Y TRANSACCIONES]")
        for i, (tx, h) in enumerate(zip(self.transacciones, hojas), 1):
            lineas.append(f" +-- T{i} ({tx})")
            lineas.append(f" |    |-- Hash H{i}: {h[:8]}... (HASH: {h})")
            
        return "\n".join(lineas)
    
    def dibujar_y_guardar_arbol(self, nombre_archivo="resultado_merkle.txt"):
        """Muestra el árbol en consola y exporta el diseño visual a un archivo .txt."""
        reporte = self.generar_reporte_texto()
        
        # Imprimir en consola
        print(reporte)
        
        # Guardar en archivo de texto plano
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(reporte)
        print(f"\n[SISTEMA] El reporte visual ha sido guardado con éxito en: '{nombre_archivo}'")

class MerkleProof:
    @staticmethod
    def verificar(prueba: list, hash_objetivo: str, raiz: str) -> bool:
        """Verifica si una prueba reconstruye con éxito la raíz provista."""
        hash_actual = hash_objetivo
        for paso in prueba:
            if paso["posicion"] == "left":
                combinado = paso["hash"] + hash_actual
            else:
                combinado = hash_actual + paso["hash"]
            hash_actual = sha256(combinado)
        return hash_actual == raiz

# Experimento (Generado usando Gemini 3.1 Pro)
if __name__ == "__main__":
    print("=== INICIANDO EXPERIMENTO ÁRBOL DE MERKLE ===\n")

    # 5 bloques de datos (transacciones simuladas)
    bloques = [
        "Tx1: Alice -> Bob 100 BTC",
        "Tx2: Bob -> Charlie 50 BTC",
        "Tx3: Charlie -> Dave 25 BTC",
        "Tx4: Dave -> Eve 10 BTC",
        "Tx5: Eve -> Alice 5 BTC"
    ]
    
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_txt = os.path.join(carpeta_actual, "diagrama_arbol.txt")
    
    # Construir el árbol y mostrar la raíz
    print("--- 1. CONSTRUCCIÓN DEL ÁRBOL ---")
    arbol = MerkelTree(bloques)
    raiz_original = arbol.get_root()
    arbol.dibujar_y_guardar_arbol(ruta_txt)
    
    # Modificar un bloque y demostrar que la raíz cambia
    print("--- 2. DEMOSTRACIÓN DE SENSIBILIDAD A CAMBIOS ---")
    bloques_hackeados = bloques.copy()
    bloques_hackeados[1] = "Tx2: Bob -> Hacker 5000 BTC"  # Bloque alterado
    
    arbol_hackeado = MerkelTree(bloques_hackeados)
    raiz_hackeada = arbol_hackeado.get_root()
    
    print(f"Raíz Original:   {raiz_original}")
    print(f"Raíz Modificada: {raiz_hackeada}")
    print(f"¿Las raíces coinciden?: {raiz_original == raiz_hackeada}\n")
    
    # Generar una prueba de inclusión para el bloque 3 y verificar que es válida
    print("--- 3. PRUEBA DE INCLUSIÓN VÁLIDA ---")
    indice_bloque_3 = 2  # El índice 2 corresponde a la Tx3 (0-indexed)
    dato_bloque_3 = bloques[indice_bloque_3]
    hash_bloque_3 = sha256(dato_bloque_3)
    
    prueba_valida = arbol.get_proof(indice_bloque_3)
    resultado_valido = MerkleProof.verificar(prueba_valida, hash_bloque_3, raiz_original)
    
    print(f"Verificando Bloque 3: '{dato_bloque_3}'")
    print(f"Resultado de verificación: {'ÉXITO (Válida)' if resultado_valido else 'FALLO (Inválida)'}\n")
    
    # Intentar verificar con un dato incorrecto -> debe fallar
    print("--- 4. PRUEBA DE INCLUSIÓN INVÁLIDA ---")
    dato_falso = "Tx3: Charlie -> Dave 9999 BTC" # Alguien intenta falsificar el bloque 3
    hash_falso = sha256(dato_falso)
    
    # Usamos la misma prueba criptográfica generada antes, pero con el hash del dato falso
    resultado_invalido = MerkleProof.verificar(prueba_valida, hash_falso, raiz_original)
    
    print(f"Intentando verificar bloque alterado: '{dato_falso}'")
    print(f"Resultado de verificación: {'ÉXITO (Válida)' if resultado_invalido else 'FALLO (Inválida)'}\n")
    
    print("=== EXPERIMENTO FINALIZADO ===")

