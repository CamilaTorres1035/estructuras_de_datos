# Laboratorio 2: Implementación de Árbol de Merkle

**Estudiante:** Maria Camila Torres Chica

## Requisitos Generales del Entorno

* **Lenguaje:** Python 3.10 o superior.
* **Dependencias principales:** Módulos estándar de Python (`hashlib`, `json`)

## Descripción

En este laboratorio se abordó la construcción de un Árbol de Merkle, diseñado para demostrar la integridad y verificación de datos.

### Problemas Resueltos

1. **Serialización Adaptativa Dinámica:** El árbol soporta cualquier estructura de datos de forma agnóstica. Evalúa si el elemento es un diccionario para aplicar `json.dumps(sort_keys=True)` o si es texto plano/valores simples para procesarlos directamente con `str()`, garantizando consistencia criptográfica en cualquier escenario.
2. **Matriz como Pila e Inmutabilidad Funcional:** El árbol se almacena internamente como una matriz bidimensional (pila de tuplas). La base (Nivel 0) contiene las hojas iniciales y cada nivel superior se apila hasta converger en la Raíz (*Merkle Root*) en el tope. Al utilizar tuplas anidadas, la estructura queda blindada como de solo lectura (*Readonly*) en tiempo de ejecución.
3. **Optimización Criptográfica de Nodos Impares:** En lugar de promover nodos sin pareja directamente al siguiente nivel, el sistema implementa el estándar oficial de redes distribuidas (estilo Bitcoin). Si una capa es impar, se duplica el último nodo intermedio antes de emparejar, garantizando niveles pares uniformes y optimizando el bucle de hash.
4. **Generación y Verificación de Pruebas (Merkle Proofs):** Capacidad de extraer de forma aislada el camino de hashes hermanos (co-ruta) para cualquier transacción y verificar su integridad de manera desacoplada sin necesidad de reconstruir o exponer el árbol completo.

## Archivos del Repositorio

| Archivo | Descripción |
| :--- | :--- |
| `arbolMerkle.py` | Implementación, dibujado y generación de pruebas de inclusión del Árbol de Merkle y caso práctico automatizado que realiza el experimento. |
| [diagrama_arbol.txt](/laboratorio-2/diagrama_arbol.txt) | Reporte persistente generado automáticamente por la clase `MerkleTree` que exporta el diseño visual jerárquico del árbol, sus niveles intermedios y las transacciones asociadas. |

## Notas aclaratorias

* La implementación del árbol de Merkle es una adaptación a python de la implementación hecha en Typescript de [software crafters](https://softwarecrafters.io/blockchain/merkle-trees-typescript-tdd)
* El bloque de experimentación fue generado con Gemini 3.1 Pro

## Evidencias (Capturas de Pantalla)

### 1. Diagrama del Árbol y Ejecución Inicial

![Diagrama del árbol](/img/construccionArbolMerkle%20(2).png)

### 2. Sensibilidad a Cambios y Pruebas de Inclusión

*(Muestra el cambio de la raíz al alterar un bloque, seguido de la verificación exitosa e inválida)*
![Pruebas de verificación](/img/verficacionesArbolMerkle.png)
