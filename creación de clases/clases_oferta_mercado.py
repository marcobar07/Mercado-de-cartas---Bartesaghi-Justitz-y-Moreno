"""
Módulo de las clases Oferta y Mercado.
"""

from datetime import datetime
from typing import List, Optional

from .clases_arma import Arma
from .clase_usuarios import Usuario


class Oferta:
    """Representa una oferta de venta en el mercado."""
    def __init__(self, vendedor: Usuario, arma: Arma, precio: int):
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
    def __init__(self):
        self.ofertas_activas: List[Oferta] = []
        self.historial: List[Oferta] = []

    def publicar_oferta(self, vendedor: Usuario, arma: Arma, precio: int) -> Oferta:
        """Crea una oferta, la añade a activas y quita el arma del inventario del vendedor."""
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
        """Procesa la compra de una oferta entre usuario y vendedor."""
        if oferta not in self.ofertas_activas:
            return False
        
        # Validar fondos del comprador
        if not comprador.gastar_fondos(oferta.precio):
            return False

        # Transferir fondos al vendedor
        oferta.vendedor.conseguir_fondos(oferta.precio)

        # Entregar arma al comprador
        comprador.agregar_arma(oferta.arma)

        # Actualizar estado de la oferta y moverla al historial
        oferta.marcar_como_vendida(comprador)
        self.ofertas_activas.remove(oferta)
        self.historial.append(oferta)
        
        return True
