"""
Módulo de funciones auxiliares, números pseudoaleatorios con semilla y
gestión integral del mercado de cartas / armas.

Este módulo cumple dos propósitos fundamentales:
1. Almacenar y alterar la semilla pseudoaleatoria para garantizar reproducibilidad.
2. Proveer las funciones globales y de orquestación que gestionan las operaciones
   reales del mercado (aperturas de cajas, publicaciones con precios sugeridos,
   compras con comisiones, cancelaciones, filtrados e informes financieros),
   invocando los métodos de cada clase del dominio (Usuario, Caja, Arma, Oferta, Mercado).
"""

from datetime import datetime
import random
from typing import List, Dict, Any, Optional

# ==========================================
# 1. GESTIÓN DE LA SEMILLA PSEUDOALEATORIA
# ==========================================

# Semilla global guardada en este documento
semilla: int = 42


def obtener_semilla() -> int:
    """Retorna el valor actual de la semilla almacenada en este documento."""
    global semilla
    return semilla


def modificar_semilla(nueva_semilla: int) -> None:
    """
    Modifica manualmente el valor de la semilla guardada.
    Permite establecer un nuevo estado inicial para la generación pseudoaleatoria.
    """
    global semilla
    semilla = nueva_semilla


def alterar_semilla() -> int:
    """
    Aplica la semilla actual a random y genera un nuevo valor para 'semilla',
    alterándola y guardándola para la próxima ejecución.
    """
    global semilla
    random.seed(semilla)
    semilla = random.randint(1, 2_147_483_647)
    return semilla


# Alias en inglés por conveniencia
get_semilla = obtener_semilla
set_semilla = modificar_semilla


def choices(poblacion: List[Any], weights: Optional[List[float]] = None, k: int = 1) -> List[Any]:
    """Selecciona k elementos con pesos, aplicando y alterando la semilla."""
    global semilla
    random.seed(semilla)
    resultado = random.choices(poblacion, weights=weights, k=k)
    semilla = random.randint(1, 2_147_483_647)
    return resultado


def uniform(a: float, b: float) -> float:
    """Genera un float en [a, b], aplicando y alterando la semilla."""
    global semilla
    random.seed(semilla)
    resultado = random.uniform(a, b)
    semilla = random.randint(1, 2_147_483_647)
    return resultado


def randint(a: int, b: int) -> int:
    """Genera un entero en [a, b], aplicando y alterando la semilla."""
    global semilla
    random.seed(semilla)
    resultado = random.randint(a, b)
    semilla = random.randint(1, 2_147_483_647)
    return resultado


def random_float() -> float:
    """Genera un float en [0.0, 1.0), aplicando y alterando la semilla."""
    global semilla
    random.seed(semilla)
    resultado = random.random()
    semilla = random.randint(1, 2_147_483_647)
    return resultado


random_val = random_float


def seleccionar_item_lootpool(lootpool: List[dict], pesos: List[float]) -> dict:
    """Selecciona un ítem del lootpool ponderado por sus probabilidades."""
    return choices(lootpool, weights=pesos, k=1)[0]


def generar_desgaste(min_val: float = 0.00, max_val: float = 1.00, decimales: int = 4) -> float:
    """Genera el desgaste del arma redondeado a los decimales especificados."""
    return round(uniform(min_val, max_val), decimales)


def generar_patron(min_val: int = 1, max_val: int = 1000) -> int:
    """Genera un patrón numérico entero para el arma entre min_val y max_val."""
    return randint(min_val, max_val)


def determinar_stattrack(probabilidad: float = 0.10) -> bool:
    """Determina si el arma obtenida tendrá tecnología StatTrak."""
    return random_float() < probabilidad


# ==========================================
# 2. ESTADO Y FUNCIONES GLOBALES DE SOPORTE
# ==========================================

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


# ==========================================
# 3. FUNCIONES DE GESTIÓN REAL DEL MERCADO
# (Orquestan flujos completos invocando métodos de cada clase)
# ==========================================

def gestionar_compra_y_apertura_caja(usuario: Any, caja: Any) -> Dict[str, Any]:
    """
    Gestiona la compra de una caja y su posterior apertura:
    1. Valida si el usuario tiene fondos para la caja con usuario.gastar_fondos().
    2. Agrega la caja al inventario con usuario.agregar_caja().
    3. Genera un ID único mediante la función global generar_siguiente_id().
    4. Abre la caja con usuario.abrir_caja() (que invoca caja.abrir() usando la semilla).
    5. Actualiza y calcula el valor del arma obtenida con arma.calcular_valor().
    6. Evalúa la rentabilidad con la función global evaluar_rentabilidad_apertura().
    7. Registra la transacción con la función global registrar_evento().
    """
    if not usuario.gastar_fondos(caja.precio):
        registrar_evento(
            tipo="ERROR_COMPRA_CAJA",
            descripcion=f"El usuario {usuario.id} no posee fondos suficientes (${usuario.fondos}) para comprar {caja.nombre} (${caja.precio}).",
            datos={"usuario": usuario.id, "fondos": usuario.fondos, "precio_caja": caja.precio}
        )
        return {
            "exito": False,
            "motivo": "Fondos insuficientes",
            "arma": None,
            "rentabilidad": None
        }

    # Asignar la caja comprada al inventario
    usuario.agregar_caja(caja)

    # Generar nuevo ID único con la función global
    nuevo_id = generar_siguiente_id()

    # Abrir la caja (consume la caja del inventario y asigna el arma obtenida)
    arma_obtenida = usuario.abrir_caja(caja, nuevo_id)

    if arma_obtenida is None:
        return {
            "exito": False,
            "motivo": "Error al abrir la caja",
            "arma": None,
            "rentabilidad": None
        }

    # Asegurar el cálculo del valor del arma llamando a su método
    arma_obtenida.calcular_valor()

    # Evaluar rentabilidad con la función global
    rentabilidad = evaluar_rentabilidad_apertura(caja.precio, arma_obtenida.valor)

    # Registrar el evento global
    registrar_evento(
        tipo="APERTURA_CAJA",
        descripcion=f"{usuario.id} abrió {caja.nombre} y obtuvo {arma_obtenida.skin} valorada en ${arma_obtenida.valor}.",
        datos={
            "usuario": usuario.id,
            "caja": caja.nombre,
            "arma_id": arma_obtenida.id,
            "arma_tipo": arma_obtenida.tipo,
            "skin": arma_obtenida.skin,
            "valor": arma_obtenida.valor,
            "rentabilidad": rentabilidad
        }
    )

    return {
        "exito": True,
        "usuario": usuario.id,
        "caja": caja.nombre,
        "arma": arma_obtenida,
        "rentabilidad": rentabilidad,
        "fondos_restantes": usuario.fondos
    }


def gestionar_publicacion_oferta(
    mercado: Any,
    vendedor: Any,
    arma: Any,
    precio_personalizado: Optional[int] = None,
    margen_sugerido: float = 0.0
) -> Dict[str, Any]:
    """
    Gestiona la publicación de un arma en el mercado:
    1. Verifica que el arma pertenezca al inventario del vendedor.
    2. Invoca arma.calcular_valor() para conocer su cotización.
    3. Si no se indica precio, calcula un precio sugerido con la función global calcular_precio_sugerido().
    4. Invoca mercado.publicar_oferta(vendedor, arma, precio).
    5. Registra el evento con la función global registrar_evento().
    """
    if arma not in vendedor.inventario_armas:
        registrar_evento(
            tipo="ERROR_PUBLICACION",
            descripcion=f"{vendedor.id} intentó publicar un arma que no está en su inventario.",
            datos={"vendedor": vendedor.id, "arma_id": getattr(arma, "id", None)}
        )
        return {"exito": False, "motivo": "El vendedor no posee el arma indicada", "oferta": None}

    # Actualizar cotización del arma llamando a su método
    valor_base = arma.calcular_valor()

    # Determinar el precio final de la oferta
    if precio_personalizado is not None and precio_personalizado > 0:
        precio_final = precio_personalizado
    else:
        precio_final = calcular_precio_sugerido(valor_base, margen_sugerido)

    # Publicar oferta a través del método de Mercado
    oferta = mercado.publicar_oferta(vendedor, arma, precio_final)

    registrar_evento(
        tipo="PUBLICACION_OFERTA",
        descripcion=f"{vendedor.id} publicó {arma.skin} en el mercado por ${precio_final}.",
        datos={
            "vendedor": vendedor.id,
            "arma_id": arma.id,
            "skin": arma.skin,
            "valor_base": valor_base,
            "precio_publicado": precio_final
        }
    )

    return {
        "exito": True,
        "oferta": oferta,
        "vendedor": vendedor.id,
        "arma": arma,
        "precio": precio_final,
        "valor_base": valor_base
    }


def gestionar_compra_oferta(
    mercado: Any,
    comprador: Any,
    oferta: Any,
    aplicar_comision: bool = True,
    tasa_comision: float = TASA_COMISION_DEFAULT
) -> Dict[str, Any]:
    """
    Gestiona de forma integral la compra de un arma publicada en el mercado:
    1. Valida que el comprador no sea el mismo vendedor (previene auto-compra).
    2. Valida que la oferta esté activa en mercado.ofertas_activas.
    3. Valida que el comprador tenga fondos suficientes.
    4. Ejecuta mercado.comprar_oferta(oferta, comprador).
    5. Si aplica comisión, calcula la comisión global con calcular_comision_mercado(),
       la retiene de los fondos del vendedor con vendedor.gastar_fondos() y la acredita
       al fondo global del mercado _fondos_comisiones_mercado.
    6. Actualiza los valores de inventario de ambos usuarios con usuario.valor_inventario().
    7. Registra el evento detallado con la función global registrar_evento().
    """
    global _fondos_comisiones_mercado

    # Validación 1: Auto-compra
    if comprador.id == oferta.vendedor.id:
        registrar_evento(
            tipo="ERROR_COMPRA_OFERTA",
            descripcion=f"{comprador.id} intentó comprar su propia oferta.",
            datos={"usuario": comprador.id, "arma": oferta.arma.skin}
        )
        return {"exito": False, "motivo": "Un usuario no puede comprar su propia oferta."}

    # Validación 2: Oferta activa
    if oferta not in mercado.ofertas_activas:
        registrar_evento(
            tipo="ERROR_COMPRA_OFERTA",
            descripcion=f"La oferta para {oferta.arma.skin} no está activa en el mercado.",
            datos={"oferta_estado": oferta.estado}
        )
        return {"exito": False, "motivo": "La oferta no está activa o ya fue procesada."}

    # Validación 3: Fondos del comprador
    if comprador.fondos < oferta.precio:
        registrar_evento(
            tipo="ERROR_COMPRA_OFERTA",
            descripcion=f"{comprador.id} no posee fondos suficientes (${comprador.fondos}) para comprar la oferta (${oferta.precio}).",
            datos={"comprador": comprador.id, "fondos": comprador.fondos, "precio": oferta.precio}
        )
        return {"exito": False, "motivo": "Fondos insuficientes del comprador."}

    precio_transaccion = oferta.precio
    vendedor = oferta.vendedor
    arma_transaccionada = oferta.arma

    # Ejecutar la compra a través del método de Mercado
    compra_exitosa = mercado.comprar_oferta(oferta, comprador)

    if not compra_exitosa:
        return {"exito": False, "motivo": "Fallo al ejecutar la compra en el mercado."}

    # Gestión de comisión del mercado
    comision = 0
    if aplicar_comision:
        comision = calcular_comision_mercado(precio_transaccion, tasa_comision)
        # Se retiene la comisión al vendedor
        if vendedor.gastar_fondos(comision):
            _fondos_comisiones_mercado += comision

    # Auditoría de valor de inventarios actualizados
    valor_inv_comprador = comprador.valor_inventario()
    valor_inv_vendedor = vendedor.valor_inventario()

    registrar_evento(
        tipo="TRANSACCION_COMPLETADA",
        descripcion=f"{comprador.id} compró {arma_transaccionada.skin} a {vendedor.id} por ${precio_transaccion} (comisión: ${comision}).",
        datos={
            "comprador": comprador.id,
            "vendedor": vendedor.id,
            "arma": arma_transaccionada.skin,
            "precio": precio_transaccion,
            "comision": comision,
            "saldo_comprador": comprador.fondos,
            "saldo_vendedor": vendedor.fondos
        }
    )

    return {
        "exito": True,
        "comprador": comprador.id,
        "vendedor": vendedor.id,
        "arma": arma_transaccionada.skin,
        "precio": precio_transaccion,
        "comision_mercado": comision,
        "saldo_comprador": comprador.fondos,
        "saldo_vendedor": vendedor.fondos,
        "valor_inventario_comprador": valor_inv_comprador,
        "valor_inventario_vendedor": valor_inv_vendedor
    }


def gestionar_cancelacion_oferta(mercado: Any, solicitante: Any, oferta: Any) -> Dict[str, Any]:
    """
    Gestiona la cancelación de una oferta:
    1. Verifica que el solicitante sea el vendedor legítimo.
    2. Invoca mercado.cancelar_oferta(oferta), devolviendo el arma al inventario.
    3. Registra el evento en la función global registrar_evento().
    """
    if solicitante.id != oferta.vendedor.id:
        registrar_evento(
            tipo="ERROR_CANCELACION",
            descripcion=f"{solicitante.id} no tiene permiso para cancelar la oferta de {oferta.vendedor.id}.",
            datos={"solicitante": solicitante.id, "vendedor": oferta.vendedor.id}
        )
        return {"exito": False, "motivo": "Solo el vendedor puede cancelar su oferta."}

    if oferta not in mercado.ofertas_activas:
        return {"exito": False, "motivo": "La oferta no se encuentra activa."}

    mercado.cancelar_oferta(oferta)

    registrar_evento(
        tipo="CANCELACION_OFERTA",
        descripcion=f"{solicitante.id} canceló su oferta por {oferta.arma.skin}. El arma regresó a su inventario.",
        datos={"vendedor": solicitante.id, "arma": oferta.arma.skin}
    )

    return {"exito": True, "oferta": oferta, "arma": oferta.arma}


def gestionar_busqueda_y_filtrado(
    mercado: Any,
    tipo_arma: Optional[str] = None,
    rareza: Optional[str] = None,
    stattrack: Optional[bool] = None,
    precio_maximo: Optional[int] = None,
    ordenar_por: str = "precio"
) -> List[Any]:
    """
    Filtra y ordena ofertas activas en el mercado según múltiples criterios:
    - tipo_arma: filtra por tipo ("Ak47", "AWP", "Glock", "ArmaBlanca", etc.)
    - rareza: filtra por rareza ("azul", "violeta", "rosada", "roja", "dorada")
    - stattrack: filtra por True o False
    - precio_maximo: filtra ofertas cuyo precio sea menor o igual al valor
    - ordenar_por: 'precio' (ascendente), 'precio_desc', o 'desgaste'
    """
    resultados = []

    for oferta in mercado.ofertas_activas:
        arma = oferta.arma

        if tipo_arma is not None and arma.tipo.lower() != tipo_arma.lower():
            continue
        if rareza is not None and arma.rareza.lower() != rareza.lower():
            continue
        if stattrack is not None and arma.stattrack != stattrack:
            continue
        if precio_maximo is not None and oferta.precio > precio_maximo:
            continue

        resultados.append(oferta)

    # Ordenamiento
    if ordenar_por == "precio":
        resultados.sort(key=lambda o: o.precio)
    elif ordenar_por == "precio_desc":
        resultados.sort(key=lambda o: o.precio, reverse=True)
    elif ordenar_por == "desgaste":
        resultados.sort(key=lambda o: o.arma.desgaste)

    return resultados


def gestionar_liquidacion_masiva(
    mercado: Any,
    usuario: Any,
    valor_maximo_corte: int,
    descuento_liquidacion: float = 0.15
) -> Dict[str, Any]:
    """
    Vende o publica en lote todas las armas de bajo valor de un usuario para obtener liquidez rápida:
    1. Recorre el inventario de armas del usuario.
    2. Para cada arma con valor <= valor_maximo_corte, calcula un precio reducido con
       la función global calcular_precio_sugerido() y margen negativo.
    3. Las publica en el mercado mediante gestionar_publicacion_oferta().
    4. Registra el resumen en el historial de eventos global.
    """
    armas_a_liquidar = [
        arma for arma in list(usuario.inventario_armas)
        if arma.calcular_valor() <= valor_maximo_corte
    ]

    ofertas_creadas = []
    for arma in armas_a_liquidar:
        res = gestionar_publicacion_oferta(
            mercado=mercado,
            vendedor=usuario,
            arma=arma,
            margen_sugerido=-descuento_liquidacion
        )
        if res["exito"]:
            ofertas_creadas.append(res["oferta"])

    registrar_evento(
        tipo="LIQUIDACION_MASIVA",
        descripcion=f"{usuario.id} liquidó {len(ofertas_creadas)} armas en el mercado.",
        datos={"usuario": usuario.id, "cantidad_liquidada": len(ofertas_creadas)}
    )

    return {
        "usuario": usuario.id,
        "total_liquidado": len(ofertas_creadas),
        "ofertas": ofertas_creadas
    }


def gestionar_informe_completo_mercado(mercado: Any, usuarios: Optional[List[Any]] = None) -> Dict[str, Any]:
    """
    Genera un informe integral del mercado:
    - Ofertas activas y volumen económico en venta.
    - Historial de transacciones concluidas y volumen transaccionado.
    - Total recaudado por comisiones del mercado (función global obtener_fondos_comisiones()).
    - Análisis de inventarios de cada usuario mediante usuario.valor_inventario().
    - Total de eventos registrados en el log global.
    """
    total_ofertas_activas = len(mercado.ofertas_activas)
    valor_acumulado_activas = sum(o.precio for o in mercado.ofertas_activas)

    ventas_concluidas = [o for o in mercado.historial if o.estado == "Vendida"]
    ofertas_canceladas = [o for o in mercado.historial if o.estado == "Cancelada"]
    volumen_ventas = sum(o.precio for o in ventas_concluidas)

    # Identificar la venta más cara
    oferta_mas_cara = max(ventas_concluidas, key=lambda o: o.precio) if ventas_concluidas else None

    # Resumen por usuarios
    resumen_usuarios = []
    if usuarios:
        for u in usuarios:
            resumen_usuarios.append({
                "usuario": u.id,
                "fondos": u.fondos,
                "cantidad_armas": len(u.inventario_armas),
                "cantidad_cajas": len(u.inventario_cajas),
                "valor_total_inventario": u.valor_inventario()
            })

    informe = {
        "ofertas_activas": total_ofertas_activas,
        "valor_en_venta_activa": valor_acumulado_activas,
        "total_ventas_concluidas": len(ventas_concluidas),
        "total_canceladas": len(ofertas_canceladas),
        "volumen_total_transaccionado": volumen_ventas,
        "fondos_comisiones_mercado": obtener_fondos_comisiones(),
        "arma_mas_cara_vendida": {
            "skin": oferta_mas_cara.arma.skin,
            "precio": oferta_mas_cara.precio,
            "comprador": oferta_mas_cara.comprador.id if oferta_mas_cara.comprador else None
        } if oferta_mas_cara else None,
        "usuarios": resumen_usuarios,
        "total_eventos_registrados": len(obtener_historial_eventos())
    }

    return informe


# ==========================================
# 4. PRUEBA RÁPIDA / DEMOSTRACIÓN DE FUNCIONES
# ==========================================

if __name__ == "__main__":
    print("=== DEMOSTRACIÓN DEL MÓDULO Funciones.py ===")
    print(f"Semilla inicial: {obtener_semilla()}")

    print("\n1. Verificando alteración y determinismo de semilla:")
    v1 = uniform(0.0, 1.0)
    print(f"   Llamada 1 -> valor={v1:.4f} | Nueva semilla={obtener_semilla()}")
    v2 = uniform(0.0, 1.0)
    print(f"   Llamada 2 -> valor={v2:.4f} | Nueva semilla={obtener_semilla()}")

    modificar_semilla(42)
    v3 = uniform(0.0, 1.0)
    print(f"   Reiniciando semilla a 42 -> valor={v3:.4f} (Coincide: {v1 == v3})")

    print("\n2. Probando funciones globales de soporte:")
    print(f"   Siguiente ID: {generar_siguiente_id()}")
    print(f"   Siguiente ID: {generar_siguiente_id()}")
    print(f"   Comisión de $1000 al 5%: ${calcular_comision_mercado(1000)}")
    print(f"   Precio sugerido para arma de $1000 (+15%): ${calcular_precio_sugerido(1000, 0.15)}")
    print(f"   Rentabilidad de abrir caja de $250 con drop de $600: {evaluar_rentabilidad_apertura(250, 600)}")
    registrar_evento("TEST", "Prueba de evento inicial")
    print(f"   Eventos registrados en log: {len(obtener_historial_eventos())}")
