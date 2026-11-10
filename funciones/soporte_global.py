"""
Módulo de estado y funciones globales de soporte para el mercado.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

# Contador global para IDs únicos de armas
_contador_id_armas: int = 1000

# Registro global de eventos y auditoría del sistema
_historial_eventos: List[Dict[str, Any]] = []

# Fondo global acumulado por comisiones del mercado
_fondos_comisiones_mercado: int = 0

# Tasa de comisión predeterminada del mercado (5%)
TASA_COMISION_DEFAULT: float = 0.05


def generar_siguiente_id() -> int:
    """Genera y retorna un ID autoincremental único a nivel global."""
    global _contador_id_armas
    _contador_id_armas += 1
    return _contador_id_armas


def registrar_evento(tipo: str, descripcion: str, datos: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Registra una acción en el historial global de auditoría del sistema."""
    global _historial_eventos
    evento = {
        "timestamp": datetime.now(),
        "tipo": tipo,
        "descripcion": descripcion,
        "datos": datos if datos is not None else {}
    }
    _historial_eventos.append(evento)
    return evento


def obtener_historial_eventos() -> List[Dict[str, Any]]:
    """Retorna una copia del historial de eventos global."""
    return list(_historial_eventos)


def limpiar_historial_eventos() -> None:
    """Limpia el registro global de eventos."""
    global _historial_eventos
    _historial_eventos.clear()


def obtener_fondos_comisiones() -> int:
    """Retorna el total de fondos acumulados por comisiones de mercado."""
    return _fondos_comisiones_mercado


def calcular_comision_mercado(monto: int, tasa: float = TASA_COMISION_DEFAULT) -> int:
    """Calcula la comisión del mercado redondeada a entero a partir de un monto y una tasa."""
    return int(monto * tasa)


def calcular_precio_sugerido(valor_base: int, margen_porcentaje: float = 0.0) -> int:
    """
    Calcula un precio de venta recomendado aplicando un margen porcentual sobre
    el valor calculado del arma (ej. +0.10 para 10% sobre el valor, -0.15 para liquidación rápida).
    """
    precio = int(valor_base * (1.0 + margen_porcentaje))
    return max(precio, 1)


def evaluar_rentabilidad_apertura(precio_caja: int, valor_arma: int) -> Dict[str, Any]:
    """Evalúa financieramente la apertura de una caja: ganancia/pérdida neta y ROI."""
    beneficio_neto = valor_arma - precio_caja
    roi_porcentaje = round((beneficio_neto / precio_caja) * 100, 2) if precio_caja > 0 else 0.0
    return {
        "precio_caja": precio_caja,
        "valor_arma": valor_arma,
        "beneficio_neto": beneficio_neto,
        "roi_porcentaje": roi_porcentaje,
        "es_rentable": beneficio_neto >= 0
    }

