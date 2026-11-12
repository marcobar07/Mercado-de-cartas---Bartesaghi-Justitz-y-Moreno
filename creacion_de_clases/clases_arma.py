"""
Módulo de clases de Armas y definición de Rarezas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict

# ==========================================
# 1. RAREZAS (Lista y Diccionario)
# ==========================================

RAREZAS: List[str] = ["azul", "violeta", "rosada", "roja", "dorada"]

VALORES_RAREZA: Dict[str, int] = {
    "azul": 100,
    "violeta": 150,
    "rosada": 300,
    "roja": 600,
    "dorada": 1000,
}


# ==========================================
# 2. CLASES DE ARMAS (Jerarquía y abstracción)
# ==========================================

class Arma(ABC):
    """Clase abstracta base para todas las armas."""
    multiplicador: float = 1.0
    stattrack_inverso: bool = False

    def __init__(self, id_arma: int, skin: str, desgaste: float, patron: int, rareza: str, stattrack: bool, tipo: Optional[str] = None):
        self.id = id_arma
        self.skin = skin
        self.tipo = tipo if tipo is not None else self.__class__.__name__
        self.desgaste = desgaste
        self.patron = patron

        rareza_normalizada = rareza.lower()
        if rareza_normalizada not in VALORES_RAREZA:
            raise ValueError(f"Rareza '{rareza}' no válida. Debe ser una de: {RAREZAS}")
        self.rareza = rareza_normalizada

        # Validación según el tipo de arma
        if self.__class__.__name__ == "ArmaBlanca":
            if self.rareza != "dorada":
                raise ValueError("Para las armas blancas la rareza debe ser 'dorada'.")
        else:
            if self.rareza == "dorada":
                raise ValueError("Las armas convencionales solo pueden ser: azul, violeta, rosada o roja.")

        self.stattrack = stattrack
        self.valor: Optional[int] = None

    def calcular_multiplicador_stattrack(self) -> float:
        """
        Retorna el multiplicador por StatTrak.
        En armas con stattrack_inverso (ArmaBlanca), si no es StatTrak es 1.5 y si es StatTrak es 1.0.
        En armas convencionales, si es StatTrak es 1.5 y si no es StatTrak es 1.0.
        """
        if self.stattrack_inverso:
            return 1.0 if self.stattrack else 1.5
        return 1.5 if self.stattrack else 1.0

    def calcular_valor(self) -> int:
        """
        Calcula el valor del arma según su rareza, patrón, desgaste, si es StatTrak
        y el multiplicador de la subclase de arma, guarda el resultado en self.valor y lo retorna.
        """
        # 1. Valor base según la Rareza obtenido del diccionario:
        base_rareza = VALORES_RAREZA[self.rareza]

        # 2. Multiplicador o bonificación por StatTrak (determinado según la subclase):
        multiplicador_stattrack = self.calcular_multiplicador_stattrack()

        # 3. Factor por desgaste (self.desgaste es un float entre 0.00 y 1.00):
        factor_desgaste = ((2 - self.desgaste)**3) / 2  

        # 4. Factor o bonificación por patrón (self.patron es un número entero entre 1 y 1000):
        factor_patron = 1 + ((self.patron / 50)**3) / 2

        # 5. Multiplicador aportado por cada subclase:
        multiplicador_subclase = self.multiplicador

        # 6. Fórmula final unificada en la clase base:
        valor_calculado = int(base_rareza * multiplicador_stattrack * factor_desgaste * factor_patron * multiplicador_subclase)

        self.valor = valor_calculado
        return self.valor


class ArmaBlanca(Arma):
    multiplicador: float = 3.0
    stattrack_inverso: bool = True

    def __init__(self, id_arma: int, skin: str, tipo: str, desgaste: float, patron: int, stattrack: bool, rareza: str = "dorada"):
        super().__init__(id_arma, skin, desgaste, patron, rareza, stattrack, tipo=tipo)


class Ak47(Arma):
    multiplicador: float = 2.0


class AWP(Arma):
    multiplicador: float = 1.5


class Glock(Arma):
    multiplicador: float = 1.2

