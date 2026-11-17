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
        if not isinstance(fondos, int) or isinstance(fondos, bool) or fondos < 0:
            raise ValueError(f"Los fondos iniciales deben ser un número entero no negativo, recibido: {fondos}")
        self._fondos: int = fondos
        self.inventario_armas: List[Arma] = []
        self.inventario_cajas: List[Caja] = []

    @property
    def fondos(self) -> int:
        """Retorna los fondos actuales del usuario (atributo de solo lectura)."""
        return self._fondos

    def conseguir_fondos(self, cantidad: int) -> None:
        """Aumenta los fondos del usuario con una cantidad positiva."""
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ValueError(f"La cantidad a acreditar debe ser un número entero estrictamente positivo, recibido: {cantidad}")
        self._fondos += cantidad

    def gastar_fondos(self, cantidad: int) -> bool:
        """Disminuye los fondos si hay saldo suficiente. La cantidad debe ser un entero no negativo."""
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 0:
            raise ValueError(f"La cantidad a gastar debe ser un número entero no negativo, recibido: {cantidad}")
        if cantidad == 0:
            return True
        if self._fondos >= cantidad:
            self._fondos -= cantidad
            return True
        return False

    def agregar_arma(self, arma: Arma) -> None:
        """Añade un arma al inventario garantizando que no esté duplicada ni pertenezca a otro usuario."""
        if arma in self.inventario_armas or any(a.id == arma.id for a in self.inventario_armas):
            raise ValueError(f"El arma '{arma.skin}' (ID: {arma.id}) ya se encuentra en el inventario de '{self.id}'.")
        if getattr(arma, "propietario", None) is not None and arma.propietario is not self:
            raise ValueError(f"El arma '{arma.skin}' (ID: {arma.id}) ya pertenece a otro usuario ({arma.propietario.id}).")
        arma.propietario = self
        self.inventario_armas.append(arma)

    def quitar_arma(self, arma: Arma) -> None:
        """Remueve un arma del inventario si existe. Lanza ValueError si no pertenece al usuario."""
        if arma not in self.inventario_armas:
            raise ValueError(f"El usuario '{self.id}' no posee el arma '{arma.skin}' (ID: {arma.id}) en su inventario.")
        self.inventario_armas.remove(arma)
        if getattr(arma, "propietario", None) is self:
            arma.propietario = None

    def agregar_caja(self, caja: Caja) -> None:
        """Añade una caja al inventario."""
        self.inventario_cajas.append(caja)

    def abrir_caja(self, caja: Caja, id_nueva_arma: Optional[int] = None, generador: Optional[Any] = None) -> Optional[Arma]:
        """Abre una caja de su inventario, la consume y agrega el arma obtenida. Si falla, restaura la caja al inventario."""
        if caja not in self.inventario_cajas:
            return None

        # Remover temporalmente la caja
        self.inventario_cajas.remove(caja)
        try:
            arma_obtenida = caja.abrir(id_nueva_arma=id_nueva_arma, generador=generador)
            if arma_obtenida is None:
                raise ValueError(f"La caja '{caja.nombre}' no produjo ninguna arma.")
            self.agregar_arma(arma_obtenida)
            return arma_obtenida
        except Exception:
            # Reversión / Rollback: devolver la caja al inventario en caso de error
            self.inventario_cajas.append(caja)
            raise

    def calcular_valor_arma(self, arma: Arma) -> int:
        """Método auxiliar simple para obtener el valor individual de un arma."""
        return arma.calcular_valor()

    def valor_inventario(self) -> int:
        """Suma el valor total de todas las armas del inventario."""
        total = 0
        for arma in self.inventario_armas:
            total += self.calcular_valor_arma(arma)
        return total
