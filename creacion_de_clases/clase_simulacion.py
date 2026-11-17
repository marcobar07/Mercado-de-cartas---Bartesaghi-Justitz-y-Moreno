"""
Módulo de la clase Simulacion.
Encapsula una instancia aislada e independiente de simulación con su Generador,
Auditor, Mercado y conjunto de usuarios.
"""

from typing import Dict, List, Optional, Any

from .clase_usuarios import Usuario
from .clases_oferta_mercado import Oferta, Mercado
from .clases_soporte import Generador, Auditor


class Simulacion:
    """
    Representa una simulación aislada.
    Cada simulación posee:
    - Una instancia de Generador (semilla y generación aleatoria aislada).
    - Una instancia de Auditor (historial de eventos y fondos de comisiones aislado).
    - Una instancia de Mercado (conectada a su propio auditor).
    - Su propio conjunto de usuarios registrados.
    """
    def __init__(self, nombre: str, semilla: int = 42):
        self.nombre: str = nombre
        self.generador: Generador = Generador(semilla=semilla)
        self.auditor: Auditor = Auditor()
        self.mercado: Mercado = Mercado(auditor=self.auditor)
        self.usuarios: Dict[str, Usuario] = {}
        self.contador_cajas: int = 1000

    def crear_usuario(self, id_usuario: str, fondos: int = 0) -> Usuario:
        """Crea un usuario dentro de esta simulación y lo registra en el auditor."""
        if id_usuario in self.usuarios:
            raise ValueError(f"Ya existe un usuario con el ID '{id_usuario}'.")
        usuario = Usuario(id_usuario=id_usuario, fondos=fondos)
        self.usuarios[id_usuario] = usuario
        self.auditor.registrar_evento(
            tipo="ALTA_USUARIO",
            descripcion=f"Se creó el usuario '{id_usuario}' con saldo inicial ${fondos:,}.",
            datos={"usuario": id_usuario, "fondos": fondos}
        )
        return usuario

    def borrar_usuario(self, id_usuario: str) -> bool:
        """
        Da de baja a un usuario:
        - Sus ofertas en el mercado se marcan como canceladas.
        - Sus pertenencias (armas, cajas y saldo) NO se transfieren a nadie y se destruyen.
        - Se registra el evento en el Auditor.
        """
        if id_usuario not in self.usuarios:
            return False

        usuario = self.usuarios[id_usuario]

        # 1. Cancelar todas las ofertas activas en el mercado sin transferir armas
        ofertas_a_cancelar = [o for o in list(self.mercado.ofertas_activas) if o.vendedor.id == usuario.id]
        for oferta in ofertas_a_cancelar:
            self.mercado.ofertas_activas.remove(oferta)
            oferta.cancelar()
            self.mercado.historial.append(oferta)

        # 2. Las pertenencias no se transfieren a nadie (se descartan)
        total_armas = len(usuario.inventario_armas)
        total_cajas = len(usuario.inventario_cajas)
        fondos_descartados = usuario.fondos

        usuario.inventario_armas.clear()
        usuario.inventario_cajas.clear()
        usuario.fondos = 0

        # 3. Eliminar de la simulación
        del self.usuarios[id_usuario]

        # 4. Registrar en Auditor
        self.auditor.registrar_evento(
            tipo="BAJA_USUARIO",
            descripcion=(
                f"El usuario '{id_usuario}' fue dado de baja. Se cancelaron {len(ofertas_a_cancelar)} oferta(s) en el mercado. "
                f"Sus pertenencias ({total_armas} armas, {total_cajas} cajas y ${fondos_descartados:,} de saldo) no se transfirieron a nadie."
            ),
            datos={
                "usuario": id_usuario,
                "ofertas_canceladas": len(ofertas_a_cancelar),
                "armas_descartadas": total_armas,
                "cajas_descartadas": total_cajas,
                "fondos_descartados": fondos_descartados
            }
        )
        return True
