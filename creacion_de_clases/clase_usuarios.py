"""
Módulo de la clase Usuario.
"""

from typing import List, Optional, Any

from .clases_arma import Arma
from .clases_caja import Caja


class Usuario:
    """Representa a un usuario del sistema (comprador y vendedor)."""
    def __init__(self, id_usuario: str, fondos: int = 0):
        self.id = id_usuario
        self.fondos = fondos
        self.inventario_armas: List[Arma] = []
        self.inventario_cajas: List[Caja] = []

    def conseguir_fondos(self, cantidad: int) -> None:
        """Aumenta los fondos del usuario."""
        self.fondos += cantidad

    def gastar_fondos(self, cantidad: int) -> bool:
        """Disminuye los fondos si hay saldo suficiente."""
        if self.fondos >= cantidad:
            self.fondos -= cantidad
            return True
        return False

    def agregar_arma(self, arma: Arma) -> None:
        """Añade un arma al inventario."""
        self.inventario_armas.append(arma)

    def quitar_arma(self, arma: Arma) -> None:
        """Remueve un arma del inventario si existe."""
        if arma in self.inventario_armas:
            self.inventario_armas.remove(arma)

    def agregar_caja(self, caja: Caja) -> None:
        """Añade una caja al inventario."""
        self.inventario_cajas.append(caja)

    def abrir_caja(self, caja: Caja, id_nueva_arma: Optional[int] = None, generador: Optional[Any] = None) -> Optional[Arma]:
        """Abre una caja de su inventario, la consume y agrega el arma obtenida."""
        if caja in self.inventario_cajas:
            self.inventario_cajas.remove(caja)
            arma_obtenida = caja.abrir(id_nueva_arma=id_nueva_arma, generador=generador)
            self.agregar_arma(arma_obtenida)
            return arma_obtenida
        return None

    def calcular_valor_arma(self, arma: Arma) -> int:
        """Método auxiliar simple para obtener el valor individual de un arma."""
        return arma.calcular_valor()

    def valor_inventario(self) -> int:
        """Suma el valor total de todas las armas del inventario."""
        total = 0
        for arma in self.inventario_armas:
            total += self.calcular_valor_arma(arma)
        return total
