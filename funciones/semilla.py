"""
Módulo de gestión de la semilla pseudoaleatoria y funciones aleatorias deterministas.
"""

import random
from typing import List, Any, Optional

# ==========================================
# GESTIÓN DE LA SEMILLA PSEUDOALEATORIA
# ==========================================

# Semilla global guardada en este módulo
semilla: int = 42


def obtener_semilla() -> int:
    """Retorna el valor actual de la semilla almacenada en este módulo."""
    global semilla
    return semilla


def modificar_semilla(nueva_semilla: int) -> None:
    """Modifica manualmente el valor de la semilla guardada."""
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
# ==========================================

def choices(poblacion: List[Any], weights: Optional[List[float]] = None, k: int = 1) -> List[Any]:
    """Selecciona k elementos con pesos, aplicando y alterando la semilla."""
    global semilla
    random.seed(semilla)
    resultado = random.choices(poblacion, weights=weights, k=k)
    semilla = random.randint(1, 2_147_483_647)
    return resultado


def uniform(a: float, b: float) -> float:
    """Genera un float en [a, b], aplicando y alterando la semilla."""
    global semilla
    random.seed(semilla)
    resultado = random.uniform(a, b)
    semilla = random.randint(1, 2_147_483_647)
    return resultado


def randint(a: int, b: int) -> int:
    """Genera un entero en [a, b], aplicando y alterando la semilla."""
    global semilla
    random.seed(semilla)
    resultado = random.randint(a, b)
    semilla = random.randint(1, 2_147_483_647)
    return resultado


def random_float() -> float:
    """Genera un float en [0.0, 1.0), aplicando y alterando la semilla."""
    global semilla
    random.seed(semilla)
    resultado = random.random()
    semilla = random.randint(1, 2_147_483_647)
    return resultado


random_val = random_float


def seleccionar_item_lootpool(lootpool: List[dict], pesos: List[float]) -> dict:
    """Selecciona un ítem del lootpool ponderado por sus probabilidades."""
    return choices(lootpool, weights=pesos, k=1)[0]


def generar_desgaste(min_val: float = 0.00, max_val: float = 1.00, decimales: int = 4) -> float:
    """Genera el desgaste del arma redondeado a los decimales especificados."""
    return round(uniform(min_val, max_val), decimales)


def generar_patron(min_val: int = 1, max_val: int = 1000) -> int:
    """Genera un patrón numérico entero para el arma entre min_val y max_val."""
    return randint(min_val, max_val)


def determinar_stattrack(probabilidad: float = 0.10) -> bool:
    """Determina si el arma obtenida tendrá tecnología StatTrak."""
    return random_float() < probabilidad

