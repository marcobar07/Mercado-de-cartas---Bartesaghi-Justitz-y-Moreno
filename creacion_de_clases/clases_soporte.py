"""
Módulo de clases de soporte para simulación: Generador y Auditor.
Encapsulan el estado que anteriormente residía en variables globales de módulo,
permitiendo ejecutar múltiples simulaciones concurrentes e independientes.
"""

import random
from datetime import datetime
from typing import List, Dict, Any, Optional


class Generador:
    """
    Encapsula el estado pseudoaleatorio y la generación de identificadores únicos.
    Permite instanciar múltiples generadores independientes con semillas y secuencias aisladas.
    """
    def __init__(self, semilla: int = 42, contador_id_inicial: int = 1000):
        self.semilla: int = semilla
        self.contador_id_armas: int = contador_id_inicial
        self._rng = random.Random(semilla)

    # ==========================================
    # GESTIÓN DE LA SEMILLA
    # ==========================================

    def obtener_semilla(self) -> int:
        """Retorna el valor actual de la semilla almacenada en esta instancia."""
        return self.semilla

    def modificar_semilla(self, nueva_semilla: int) -> None:
        """Modifica manualmente el valor de la semilla y reconfigura el generador."""
        self.semilla = nueva_semilla
        self._rng.seed(nueva_semilla)

    def alterar_semilla(self) -> int:
        """
        Aplica la semilla actual y genera un nuevo valor para 'semilla',
        alterándola y guardándola para la próxima operación.
        """
        self._rng.seed(self.semilla)
        self.semilla = self._rng.randint(1, 2_147_483_647)
        return self.semilla

    # Alias por conveniencia
    get_semilla = obtener_semilla
    set_semilla = modificar_semilla

    # ==========================================
    # OPERACIONES ALEATORIAS DETERMINISTAS
    # ==========================================

    def choices(self, poblacion: List[Any], weights: Optional[List[float]] = None, k: int = 1) -> List[Any]:
        """Selecciona k elementos con pesos, aplicando y alterando la semilla."""
        self._rng.seed(self.semilla)
        resultado = self._rng.choices(poblacion, weights=weights, k=k)
        self.semilla = self._rng.randint(1, 2_147_483_647)
        return resultado

    def uniform(self, a: float, b: float) -> float:
        """Genera un float en [a, b], aplicando y alterando la semilla."""
        self._rng.seed(self.semilla)
        resultado = self._rng.uniform(a, b)
        self.semilla = self._rng.randint(1, 2_147_483_647)
        return resultado

    def randint(self, a: int, b: int) -> int:
        """Genera un entero en [a, b], aplicando y alterando la semilla."""
        self._rng.seed(self.semilla)
        resultado = self._rng.randint(a, b)
        self.semilla = self._rng.randint(1, 2_147_483_647)
        return resultado

    def random_float(self) -> float:
        """Genera un float en [0.0, 1.0), aplicando y alterando la semilla."""
        self._rng.seed(self.semilla)
        resultado = self._rng.random()
        self.semilla = self._rng.randint(1, 2_147_483_647)
        return resultado

    random_val = random_float

    def seleccionar_item_lootpool(self, lootpool: List[Dict[str, Any]], pesos: List[float]) -> Dict[str, Any]:
        """Selecciona un ítem del lootpool ponderado por sus probabilidades."""
        return self.choices(lootpool, weights=pesos, k=1)[0]

    def generar_desgaste(self, min_val: float = 0.00, max_val: float = 1.00, decimales: int = 4) -> float:
        """Genera el desgaste del arma redondeado a los decimales especificados."""
        return round(self.uniform(min_val, max_val), decimales)

    def generar_patron(self, min_val: int = 1, max_val: int = 1000) -> int:
        """Genera un patrón numérico entero para el arma entre min_val y max_val."""
        return self.randint(min_val, max_val)

    def determinar_stattrack(self, probabilidad: float = 0.10) -> bool:
        """Determina si el arma obtenida tendrá tecnología StatTrak."""
        return self.random_float() < probabilidad

    # ==========================================
    # GESTIÓN DE IDENTIFICADORES ÚNICOS
    # ==========================================

    def generar_siguiente_id(self) -> int:
        """Genera y retorna un ID autoincremental único en este generador."""
        self.contador_id_armas += 1
        return self.contador_id_armas

    def obtener_contador_id(self) -> int:
        """Retorna el contador de IDs actual."""
        return self.contador_id_armas


class Auditor:
    """
    Encapsula el historial de eventos, comisiones de mercado y soporte financiero.
    Permite auditar simulaciones de forma completamente aislada.
    """
    TASA_COMISION_DEFAULT: float = 0.05

    def __init__(self, tasa_comision_default: float = TASA_COMISION_DEFAULT):
        self.historial_eventos: List[Dict[str, Any]] = []
        self.fondos_comisiones_mercado: int = 0
        self.tasa_comision_default: float = tasa_comision_default

    # ==========================================
    # REGISTRO Y GESTIÓN DE EVENTOS
    # ==========================================

    def registrar_evento(self, tipo: str, descripcion: str, datos: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Registra una acción en el historial de auditoría de este auditor."""
        evento = {
            "timestamp": datetime.now(),
            "tipo": tipo,
            "descripcion": descripcion,
            "datos": datos if datos is not None else {}
        }
        self.historial_eventos.append(evento)
        return evento

    def obtener_historial_eventos(self) -> List[Dict[str, Any]]:
        """Retorna una copia del historial de eventos de este auditor."""
        return list(self.historial_eventos)

    def limpiar_historial_eventos(self) -> None:
        """Limpia el registro de eventos de este auditor."""
        self.historial_eventos.clear()

    # ==========================================
    # FONDOS Y COMISIONES DE MERCADO
    # ==========================================

    def obtener_fondos_comisiones(self) -> int:
        """Retorna el total de fondos acumulados por comisiones en este auditor."""
        return self.fondos_comisiones_mercado

    def acumular_comision(self, monto: int) -> None:
        """Acumula una comisión cobrada en los fondos del mercado."""
        self.fondos_comisiones_mercado += monto

    def calcular_comision_mercado(self, monto: int, tasa: Optional[float] = None) -> int:
        """Calcula la comisión del mercado redondeada a entero a partir de un monto y una tasa."""
        t = self.tasa_comision_default if tasa is None else tasa
        return int(monto * t)

    # ==========================================
    # CÁLCULOS FINANCIEROS AUXILIARES
    # ==========================================

    @staticmethod
    def calcular_precio_sugerido(valor_base: int, margen_porcentaje: float = 0.0) -> int:
        """
        Calcula un precio de venta recomendado aplicando un margen porcentual sobre
        el valor calculado del arma.
        """
        precio = int(valor_base * (1.0 + margen_porcentaje))
        return max(precio, 1)

    @staticmethod
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

