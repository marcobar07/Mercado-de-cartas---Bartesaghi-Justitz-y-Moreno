"""
Módulo de funciones auxiliares y manejo de números pseudoaleatorios con semilla.

Este módulo almacena, gestiona y altera una semilla global para controlar
todas las operaciones de generación de valores aleatorios (selección de drops,
desgaste, patrones, StatTrak, etc.) de forma determinista y reproducible.
"""

import random
from typing import List, Any, Optional

# ==========================================
# GESTIÓN DE LA SEMILLA
# ==========================================

# Semilla inicial por defecto guardada en el documento
semilla: int = 42


def obtener_semilla() -> int:
    """Retorna el valor actual de la semilla almacenada en este documento."""
    global semilla
    return semilla


def modificar_semilla(nueva_semilla: int) -> None:
    """
    Modifica manualmente el valor de la semilla guardada.
    Permite establecer un nuevo estado inicial para la generación pseudoaleatoria.
    """
    global semilla
    semilla = nueva_semilla


def alterar_semilla() -> int:
    """
    Aplica la semilla actual a random y genera un nuevo valor para 'semilla',
    alterándola y guardándola para la próxima ejecución.
    """
    global semilla
    random.seed(semilla)
    semilla = random.randint(1, 2_147_483_647)
    return semilla


# Alias en inglés por conveniencia
get_semilla = obtener_semilla
set_semilla = modificar_semilla


# ==========================================
# FUNCIONES ALEATORIAS BASADAS EN SEMILLA
# (La semilla se aplica y se altera en cada llamada)
# ==========================================

def choices(poblacion: List[Any], weights: Optional[List[float]] = None, k: int = 1) -> List[Any]:
    """
    Selecciona k elementos de una población considerando ponderaciones (weights).
    Utiliza la semilla actual y la altera para la siguiente llamada.
    """
    global semilla
    random.seed(semilla)
    resultado = random.choices(poblacion, weights=weights, k=k)
    # Se altera y guarda la nueva semilla
    semilla = random.randint(1, 2_147_483_647)
    return resultado


def uniform(a: float, b: float) -> float:
    """
    Genera un número flotante pseudoaleatorio en el rango [a, b].
    Utiliza la semilla actual y la altera para la siguiente llamada.
    """
    global semilla
    random.seed(semilla)
    resultado = random.uniform(a, b)
    # Se altera y guarda la nueva semilla
    semilla = random.randint(1, 2_147_483_647)
    return resultado


def randint(a: int, b: int) -> int:
    """
    Genera un número entero pseudoaleatorio en el rango [a, b].
    Utiliza la semilla actual y la altera para la siguiente llamada.
    """
    global semilla
    random.seed(semilla)
    resultado = random.randint(a, b)
    # Se altera y guarda la nueva semilla
    semilla = random.randint(1, 2_147_483_647)
    return resultado


def random_float() -> float:
    """
    Genera un float pseudoaleatorio en el rango [0.0, 1.0).
    Equivalente a random.random().
    Utiliza la semilla actual y la altera para la siguiente llamada.
    """
    global semilla
    random.seed(semilla)
    resultado = random.random()
    # Se altera y guarda la nueva semilla
    semilla = random.randint(1, 2_147_483_647)
    return resultado


# Alias compatible con random.random
random_val = random_float


# ==========================================
# FUNCIONES SEMÁNTICAS ESPECÍFICAS DEL PROYECTO
# ==========================================

def seleccionar_item_lootpool(lootpool: List[dict], pesos: List[float]) -> dict:
    """Selecciona un ítem del lootpool ponderado por sus probabilidades."""
    return choices(lootpool, weights=pesos, k=1)[0]


def generar_desgaste(min_val: float = 0.00, max_val: float = 1.00, decimales: int = 4) -> float:
    """Genera el desgaste del arma redondeado a la cantidad de decimales especificada."""
    return round(uniform(min_val, max_val), decimales)


def generar_patron(min_val: int = 1, max_val: int = 1000) -> int:
    """Genera un patrón numérico entero para el arma entre min_val y max_val."""
    return randint(min_val, max_val)


def determinar_stattrack(probabilidad: float = 0.10) -> bool:
    """Determina si el arma obtenida tendrá tecnología StatTrak."""
    return random_float() < probabilidad


# ==========================================
# PRUEBA RÁPIDA / DEMOSTRACIÓN
# ==========================================

if __name__ == "__main__":
    print("=== DEMOSTRACIÓN DE SEMILLA EN Funciones.py ===")
    print(f"Semilla inicial: {obtener_semilla()}")

    print("\n1. Generando 3 números pseudoaleatorios y observando el cambio de semilla:")
    for i in range(1, 4):
        valor = uniform(0.0, 1.0)
        print(f"   Llamada {i}: valor={valor:.4f} | Nueva semilla guardada={obtener_semilla()}")

    print("\n2. Reiniciando la semilla a 42 para comprobar reproducibilidad:")
    modificar_semilla(42)
    print(f"   Semilla reiniciada a: {obtener_semilla()}")
    valor_reproducido = uniform(0.0, 1.0)
    print(f"   Primer valor con semilla 42 de nuevo: {valor_reproducido:.4f}")
    print(f"   Nueva semilla tras la llamada: {obtener_semilla()}")


