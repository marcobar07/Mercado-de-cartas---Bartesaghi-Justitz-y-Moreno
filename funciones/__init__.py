"""
Paquete funciones.
Exporta unificadamente:
1. Gestión de la semilla pseudoaleatoria (semilla.py)
2. Estado y funciones globales de soporte (soporte_global.py)
3. Funciones de gestión real del mercado (gestion_mercado.py)
"""

from .semilla import (
    semilla,
    obtener_semilla,
    modificar_semilla,
    alterar_semilla,
    get_semilla,
    set_semilla,
    choices,
    uniform,
    randint,
    random_float,
    random_val,
    seleccionar_item_lootpool,
    generar_desgaste,
    generar_patron,
    determinar_stattrack,
)

from .soporte_global import (
    generar_siguiente_id,
    registrar_evento,
    obtener_historial_eventos,
    limpiar_historial_eventos,
    obtener_fondos_comisiones,
    calcular_comision_mercado,
    calcular_precio_sugerido,
    evaluar_rentabilidad_apertura,
    TASA_COMISION_DEFAULT,
)

from .gestion_mercado import (
    gestionar_compra_y_apertura_caja,
    gestionar_publicacion_oferta,
    gestionar_compra_oferta,
    gestionar_cancelacion_oferta,
    gestionar_busqueda_y_filtrado,
    gestionar_liquidacion_masiva,
    gestionar_informe_completo_mercado,
)

__all__ = [
    # Semilla
    "semilla",
    "obtener_semilla",
    "modificar_semilla",
    "alterar_semilla",
    "get_semilla",
    "set_semilla",
    "choices",
    "uniform",
    "randint",
    "random_float",
    "random_val",
    "seleccionar_item_lootpool",
    "generar_desgaste",
    "generar_patron",
    "determinar_stattrack",
    # Soporte global
    "generar_siguiente_id",
    "registrar_evento",
    "obtener_historial_eventos",
    "limpiar_historial_eventos",
    "obtener_fondos_comisiones",
    "calcular_comision_mercado",
    "calcular_precio_sugerido",
    "evaluar_rentabilidad_apertura",
    "TASA_COMISION_DEFAULT",
    # Gestión del mercado
    "gestionar_compra_y_apertura_caja",
    "gestionar_publicacion_oferta",
    "gestionar_compra_oferta",
    "gestionar_cancelacion_oferta",
    "gestionar_busqueda_y_filtrado",
    "gestionar_liquidacion_masiva",
    "gestionar_informe_completo_mercado",
]

