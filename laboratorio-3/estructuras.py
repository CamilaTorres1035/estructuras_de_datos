# Implementación con lista nativa

from bisect import bisect_left, bisect_right
import math


class ListaEstudiantes:
    def __init__(self):
        self.estudiantes = []
    
    def insertar(self, estudiante):
        self.estudiantes.append(estudiante)
    
    def buscar(self, id):
        for est in self.estudiantes:
            if est.Id == id:
                return est
        return None
    
    def listar_ordenado(self):
        return sorted(self.estudiantes, key= lambda est: est.Id)
    
    def buscar_rango(self, id_i, id_f):
        return [est for est in self.estudiantes if id_i <= est.Id <= id_f]

# Implementación con ABB co-generado con copilot

class NodoABB:
    def __init__(self, estudiante) -> None:
        self.estudiante = estudiante
        self.izq = None
        self.der = None

class ABB:
    def __init__(self) -> None:
        self.root = None
    
    def insertar(self, estudiante):
        nuevo_nodo = NodoABB(estudiante)

        # Si el árbol está vacío
        if self.root is None:
            self.root = nuevo_nodo
            return
        
        nodo_actual = self.root

        while True:
            # No se insertan IDs duplicados, en este caso se actualiza el estudiante
            if estudiante.Id == nodo_actual.estudiante.Id:
                nodo_actual.estudiante = estudiante
                return
            # Ir hacia la izquierda
            if estudiante.Id < nodo_actual.estudiante.Id:
                if nodo_actual.izq is None:
                    nodo_actual.izq = nuevo_nodo
                    return

                nodo_actual = nodo_actual.izq
            # Ir hacia la derecha
            else:
                if nodo_actual.der is None:
                    nodo_actual.der = nuevo_nodo
                    return

                nodo_actual = nodo_actual.der
    
    def buscar(self, id):
        actual = self.root
        while actual is not None:
            if id == actual.estudiante.Id:
                return actual.estudiante
            if id < actual.estudiante.Id:
                actual = actual.izq
            elif id > actual.estudiante.Id:
                actual = actual.der
        return None
    
    def listar_ordenado(self):
        resultado = []
        pila = []
        nodo_actual = self.root

        # Recorrido inorden iterativo
        while pila or nodo_actual is not None:
            while nodo_actual is not None:
                pila.append(nodo_actual)
                nodo_actual = nodo_actual.izq

            nodo_actual = pila.pop()
            resultado.append(nodo_actual.estudiante)

            nodo_actual = nodo_actual.der

        return resultado
    
    def buscar_rango(self, id_i, id_f):
        resultado = []
        pila = []
        actual = self.root
        
        while True:
            if actual is not None:
                pila.append(actual)
                if actual.estudiante.Id >= id_i:
                    actual = actual.izq
                else:
                    actual = None
            elif pila:
                actual = pila.pop()
                if id_i <= actual.estudiante.Id <= id_f:
                    resultado.append(actual.estudiante)
                if actual.estudiante.Id < id_f:
                    actual = actual.der
                else:
                    actual = None
            else:
                break
        
        return resultado
    
    def altura(self):
            # Altura = número de niveles del árbol (iterativo: con IDs ordenados la altura llega a N)
            if self.root is None:
                return 0
            maximo, pila = 0, [(self.root, 1)]
            while pila:
                nodo, nivel = pila.pop()
                maximo = max(maximo, nivel)
                if nodo.izq is not None:
                    pila.append((nodo.izq, nivel + 1))
                if nodo.der is not None:
                    pila.append((nodo.der, nivel + 1))
            return maximo

# Implementación con Árbol B+

class NodoBplus:
    def __init__(self, order):
        self.order = order
        self.values = [] # En hojas: IDs; en nodos internos: separadores
        self.keys = [] # En hojas: estudiantes; en nodos internos: hijos
        self.nextKey = None # Enlace entre hojas
        self.parent = None
        self.checkLeaf = False

    def insert_at_leaf(self, leaf, value, estudiante):
        if self.values:
            for i in range(len(self.values)):
                if value == self.values[i]:
                    # Si el ID ya existes se actualiza el estudiante
                    self.keys[i] = estudiante
                    return
                elif value < self.values[i]:
                    self.values.insert(i, value)
                    self.keys.insert(i, estudiante)
                    return
                elif i+ 1 == len(self.values):
                    self.values.append(value)
                    self.keys.append(estudiante)
                    return
        else:
            self.values = [value]
            self.keys = [estudiante]

class BplusTree:
    def __init__(self, order) -> None:
        self.root = NodoBplus(order)
        self.root.checkLeaf = True
    
    def insertar(self, estudiante):
        value = estudiante.Id
        old_node = self.search(value)
        old_node.insert_at_leaf(old_node, value, estudiante)
        
        if len(old_node.values) == old_node.order:
            node1 = NodoBplus(old_node.order)
            node1.checkLeaf = True
            node1.parent = old_node.parent
            
            mid = int(math.ceil(old_node.order/2))-1
            
            # Parte derecha se mueve a la nueva hoja
            node1.values = old_node.values[mid + 1:]
            node1.keys = old_node.keys[mid + 1:]
            node1.nextKey = old_node.nextKey

            # Parte izquierda se queda en la hoja vieja
            old_node.values = old_node.values[:mid + 1]
            old_node.keys = old_node.keys[:mid + 1]
            old_node.nextKey = node1
            
            self.insert_in_parent(old_node, node1.values[0], node1)
    
    def search(self, value):
        current_node = self.root

        while current_node.checkLeaf == False:
            # bisect_right nos da directamente el índice del puntero hijo que debemos seguir
            i = bisect_right(current_node.values, value)
            current_node = current_node.keys[i]

        return current_node
    
    def buscar(self, id):
        node = self.search(id) # Hoja donde deberia encontrarse
        # Buscamos la posición exacta del ID dentro de la hoja
        i = bisect_left(node.values, id)
        
        if i < len(node.values) and node.values[i] == id:
            return node.keys[i]
        
        return None
    
    def listar_ordenado(self):
        resultado = []

        nodo = self.root
        while nodo.checkLeaf == False:
            nodo = nodo.keys[0]

        while nodo is not None:
            for estudiante in nodo.keys:
                resultado.append(estudiante)
            nodo = nodo.nextKey

        return resultado
    
    def insert_in_parent(self, n, value, ndash):
        if self.root == n:
            rootNode = NodoBplus(n.order)
            rootNode.values = [value]
            rootNode.keys = [n, ndash]
            self.root = rootNode
            n.parent = rootNode
            ndash.parent = rootNode
            return

        parentNode = n.parent

        for i in range(len(parentNode.keys)):
            if parentNode.keys[i] == n:
                parentNode.values = parentNode.values[:i] + [value] + parentNode.values[i:]
                parentNode.keys = parentNode.keys[:i + 1] + [ndash] + parentNode.keys[i + 1:]

                if len(parentNode.keys) > parentNode.order:
                    parentdash = NodoBplus(parentNode.order)
                    parentdash.parent = parentNode.parent

                    mid = int(math.ceil(parentNode.order / 2)) - 1

                    parentdash.values = parentNode.values[mid + 1:]
                    parentdash.keys = parentNode.keys[mid + 1:]

                    value_ = parentNode.values[mid]

                    if mid == 0:
                        parentNode.values = parentNode.values[:mid + 1]
                    else:
                        parentNode.values = parentNode.values[:mid]

                    parentNode.keys = parentNode.keys[:mid + 1]

                    for j in parentNode.keys:
                        j.parent = parentNode

                    for j in parentdash.keys:
                        j.parent = parentdash

                    self.insert_in_parent(parentNode, value_, parentdash)

                return
    
    def buscar_rango(self, id_i, id_f):
        resultado = []
        
        actual = self.search(id_i)
        
        if actual is None:
            return resultado
        
        while actual is not None:
            for i in range(len(actual.values)):
                id_guardado = actual.values[i]
                if id_i <= id_guardado <= id_f:
                    resultado.append(actual.keys[i])
                elif id_guardado > id_f:
                    return resultado
            actual = actual.nextKey
        
        return resultado
    
    def altura(self):
            # En un B+ todas las hojas están al mismo nivel: basta bajar por el primer hijo
            nivel, nodo = 1, self.root
            while not nodo.checkLeaf:
                nodo = nodo.keys[0]
                nivel += 1
            return nivel

