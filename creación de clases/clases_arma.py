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

    def calcular_valor(self) -> int:
        """
        Calcula el valor del arma según su rareza, patrón, desgaste y si es StatTrak,
        guarda el resultado en self.valor y lo retorna.
        """
        # 1. Valor base según la Rareza obtenido del diccionario:
        base_rareza = VALORES_RAREZA[self.rareza]

        # 2. Multiplicador o bonificación por StatTrak:
        multiplicador_stattrack = 1.5 if self.stattrack else 1.0  

        # 3. Factor por desgaste (self.desgaste es un float entre 0.00 y 1.00):
        factor_desgaste = ((2 - self.desgaste)**3) / 2  

        # 4. Factor o bonificación por patrón (self.patron es un número entero entre 1 y 1000):
        factor_patron = 1 + ((self.patron / 50)**3) / 2

        # 5. Fórmula final
        valor_calculado = int(base_rareza * multiplicador_stattrack * factor_desgaste * factor_patron)

        self.valor = valor_calculado
        return self.valor


class ArmaBlanca(Arma):
    def __init__(self, id_arma: int, skin: str, tipo: str, desgaste: float, patron: int, stattrack: bool, rareza: str = "dorada"):
        super().__init__(id_arma, skin, desgaste, patron, rareza, stattrack, tipo=tipo)

    def calcular_valor(self) -> int:
        super().calcular_valor()
        multiplicador_stattrack = 1.5 if self.stattrack else 1.0 
        self.valor = int(self.valor / multiplicador_stattrack)  
        multiplicador_inverso = 1.0 if self.stattrack else 1.5 
        self.valor = int(self.valor * 3 * multiplicador_inverso)
        return self.valor


class Ak47(Arma):
    def calcular_valor(self) -> int:
        super().calcular_valor()
        self.valor = int(self.valor * 2)
        return self.valor


class AWP(Arma):
    def calcular_valor(self) -> int:
        super().calcular_valor()
        self.valor = int(self.valor * 1.5)
        return self.valor


class Glock(Arma):
    def calcular_valor(self) -> int:
        super().calcular_valor()
        self.valor = int(self.valor * 1.2)
        return self.valor

