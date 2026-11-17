"""
Módulo de las clases Oferta y Mercado.
"""

from datetime import datetime
from typing import List, Optional, Any

from .clases_arma import Arma
from .clase_usuarios import Usuario


class Oferta:
    """Representa una oferta de venta en el mercado."""
    def __init__(self, vendedor: Usuario, arma: Arma, precio: int):
        if not isinstance(precio, int) or isinstance(precio, bool) or precio <= 0:
            raise ValueError(f"El precio de la oferta debe ser un número entero positivo mayor a 0, recibido: {precio}")
        self.vendedor = vendedor
        self.arma = arma
        self.estado = "En venta"  # "En venta", "Vendida", "Cancelada"
        self.precio = precio
        self.fecha_publicacion = datetime.now()
        self.fecha_cierre: Optional[datetime] = None
        self.comprador: Optional[Usuario] = None

    def marcar_como_vendida(self, comprador: Usuario) -> None:
        """Método simple para actualizar el estado de la oferta a vendida."""
        self.estado = "Vendida"
        self.comprador = comprador
        self.fecha_cierre = datetime.now()

    def cancelar(self) -> None:
        """Método simple para cancelar la oferta."""
        self.estado = "Cancelada"
        self.fecha_cierre = datetime.now()


class Mercado:
    """Gestiona las ofertas activas y el historial de transacciones."""
    def __init__(self, auditor: Optional[Any] = None):
        self.ofertas_activas: List[Oferta] = []
        self.historial: List[Oferta] = []
        self.auditor = auditor

    def publicar_oferta(self, vendedor: Usuario, arma: Arma, precio: int) -> Oferta:
        """Crea una oferta, la añade a activas y quita el arma del inventario del vendedor."""
        if not isinstance(precio, int) or isinstance(precio, bool) or precio <= 0:
            raise ValueError(f"El precio de la oferta debe ser un número entero positivo mayor a 0, recibido: {precio}")
        if arma not in vendedor.inventario_armas:
            raise ValueError(f"El vendedor '{vendedor.id}' no posee el arma '{arma.skin}' (ID: {arma.id}) en su inventario.")
        vendedor.quitar_arma(arma)
        nueva_oferta = Oferta(vendedor, arma, precio)
        self.ofertas_activas.append(nueva_oferta)
        return nueva_oferta

    def cancelar_oferta(self, oferta: Oferta) -> None:
        """Pasa una oferta de activas al historial como cancelada y devuelve el arma al vendedor."""
        if oferta in self.ofertas_activas:
            self.ofertas_activas.remove(oferta)
            oferta.cancelar()
            oferta.vendedor.agregar_arma(oferta.arma)
            self.historial.append(oferta)

    def comprar_oferta(self, oferta: Oferta, comprador: Usuario) -> bool:
        """Procesa la compra de una oferta entre usuario y vendedor con seguridad transaccional."""
        if oferta not in self.ofertas_activas:
            return False

        if comprador.id == oferta.vendedor.id:
            return False

        # Validar fondos del comprador
        if not comprador.gastar_fondos(oferta.precio):
            return False

        # Transferir fondos al vendedor
        oferta.vendedor.conseguir_fondos(oferta.precio)

        # Entregar arma al comprador con reversión ante fallos
        try:
            comprador.agregar_arma(oferta.arma)
        except Exception:
            # Reversión monetaria completa si la entrega del arma no se concreta
            comprador.conseguir_fondos(oferta.precio)
            oferta.vendedor.gastar_fondos(oferta.precio)
            raise

        # Actualizar estado de la oferta y moverla al historial
        oferta.marcar_como_vendida(comprador)
        self.ofertas_activas.remove(oferta)
        self.historial.append(oferta)

        return True
