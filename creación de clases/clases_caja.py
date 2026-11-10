"""
Módulo de clases de Cajas de Loot.
"""

from abc import ABC
from typing import List, Dict, Any

import funciones as funciones
from .clases_arma import Arma, ArmaBlanca, Ak47, AWP, Glock


class Caja(ABC):
    """Clase abstracta base para las cajas de loot."""
    def __init__(self, id_caja: int, nombre: str, lootpool: List[Dict[str, Any]], precio: int):
        self.id = id_caja
        self.nombre = nombre
        self.lootpool = lootpool
        self.precio = precio

    def abrir(self, id_nueva_arma: int) -> Arma:
        """
        Selecciona un ítem del lootpool según sus probabilidades,
        genera sus atributos aleatorios (desgaste, patrón, stattrack)
        utilizando las funciones basadas en semilla de Funciones.py,
        y devuelve una nueva instancia del arma calculando su valor.
        """
        if not self.lootpool:
            raise ValueError(f"La caja '{self.nombre}' no tiene ítems en su lootpool.")

        # 1. Selección ponderada por probabilidad
        pesos = [item["probabilidad"] for item in self.lootpool]
        item_elegido = funciones.choices(self.lootpool, weights=pesos, k=1)[0]

        # 2. Generación de atributos aleatorios del drop
        desgaste = round(funciones.uniform(0.00, 1.00), 4)
        patron = funciones.randint(1, 1000)
        stattrack = funciones.random_float() < 0.10  # 10% de probabilidad de ser StatTrak

        # 3. Instanciación del arma según su clase
        ClaseArma = item_elegido["clase"]

        if ClaseArma is ArmaBlanca:
            arma = ClaseArma(
                id_arma=id_nueva_arma,
                skin=item_elegido["skin"],
                tipo=item_elegido.get("subtipo", "Cuchillo"),
                desgaste=desgaste,
                patron=patron,
                stattrack=stattrack
            )
        else:
            arma = ClaseArma(
                id_arma=id_nueva_arma,
                skin=item_elegido["skin"],
                desgaste=desgaste,
                patron=patron,
                rareza=item_elegido["rareza"],
                stattrack=stattrack
            )

        # 4. Cálculo de su valor monetario
        arma.calcular_valor()
        return arma


class Kilovatio(Caja):
    PRECIO_FIJO = 250
    LOOTPOOL: List[Dict[str, Any]] = [
        {"clase": Glock, "skin": "Block-18", "rareza": "azul", "probabilidad": 79.92, "subtipo": None},
        {"clase": Glock, "skin": "High Beam", "rareza": "violeta", "probabilidad": 15.98, "subtipo": None},
        {"clase": AWP, "skin": "Capillary", "rareza": "rosada", "probabilidad": 3.20, "subtipo": None},
        {"clase": Ak47, "skin": "Inheritance", "rareza": "roja", "probabilidad": 0.32, "subtipo": None},
        {"clase": AWP, "skin": "Chrome Cannon", "rareza": "roja", "probabilidad": 0.32, "subtipo": None},
        {"clase": ArmaBlanca, "subtipo": "Kukri", "skin": "Fade", "rareza": "dorada", "probabilidad": 0.13},
        {"clase": ArmaBlanca, "subtipo": "Kukri", "skin": "Slaughter", "rareza": "dorada", "probabilidad": 0.13},
    ]

    def __init__(self, id_caja: int):
        super().__init__(
            id_caja=id_caja,
            nombre="Caja Kilovatio",
            lootpool=list(self.LOOTPOOL),
            precio=self.PRECIO_FIJO
        )


class DreamsAndNightmares(Caja):
    PRECIO_FIJO = 300
    LOOTPOOL: List[Dict[str, Any]] = [
        {"clase": Glock, "skin": "Clear Polymer", "rareza": "azul", "probabilidad": 79.92, "subtipo": None},
        {"clase": AWP, "skin": "Exoskeleton", "rareza": "violeta", "probabilidad": 15.98, "subtipo": None},
        {"clase": Glock, "skin": "Snack Attack", "rareza": "rosada", "probabilidad": 3.20, "subtipo": None},
        {"clase": Ak47, "skin": "Nightwish", "rareza": "roja", "probabilidad": 0.64, "subtipo": None},
        {"clase": ArmaBlanca, "subtipo": "Mariposa", "skin": "Lore", "rareza": "dorada", "probabilidad": 0.13},
        {"clase": ArmaBlanca, "subtipo": "Bowie", "skin": "Gamma Doppler", "rareza": "dorada", "probabilidad": 0.13},
    ]

    def __init__(self, id_caja: int):
        super().__init__(
            id_caja=id_caja,
            nombre="Caja Sueños y Pesadillas",
            lootpool=list(self.LOOTPOOL),
            precio=self.PRECIO_FIJO
        )


class Revolucion(Caja):
    PRECIO_FIJO = 350
    LOOTPOOL: List[Dict[str, Any]] = [
        {"clase": Glock, "skin": "Winterized", "rareza": "azul", "probabilidad": 79.92, "subtipo": None},
        {"clase": Glock, "skin": "Umbral Hare", "rareza": "violeta", "probabilidad": 15.98, "subtipo": None},
        {"clase": AWP, "skin": "Duality", "rareza": "rosada", "probabilidad": 3.20, "subtipo": None},
        {"clase": Ak47, "skin": "Head Shot", "rareza": "roja", "probabilidad": 0.64, "subtipo": None},
        {"clase": ArmaBlanca, "subtipo": "Karambit", "skin": "Doppler", "rareza": "dorada", "probabilidad": 0.13},
        {"clase": ArmaBlanca, "subtipo": "Mariposa", "skin": "Tiger Tooth", "rareza": "dorada", "probabilidad": 0.13},
    ]

    def __init__(self, id_caja: int):
        super().__init__(
            id_caja=id_caja,
            nombre="Caja Revolución",
            lootpool=list(self.LOOTPOOL),
            precio=self.PRECIO_FIJO
        )
