"""
Módulo de funciones de gestión real del mercado (orquestación de clases).
"""

from typing import List, Dict, Any, Optional

from .soporte_global import (
    generar_siguiente_id,
    registrar_evento,
    obtener_historial_eventos,
    obtener_fondos_comisiones,
    calcular_comision_mercado,
    calcular_precio_sugerido,
    evaluar_rentabilidad_apertura,
    TASA_COMISION_DEFAULT,
)


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
       la retiene de los fondos del vendedor con vendedor.gastar_fondos().
    6. Actualiza los valores de inventario de ambos usuarios con usuario.valor_inventario().
    7. Registra el evento detallado con la función global registrar_evento().
    """
    import funciones.soporte_global as soporte

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
        if vendedor.gastar_fondos(comision):
            soporte._fondos_comisiones_mercado += comision

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
    - tipo_arma, rareza, stattrack, precio_maximo
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
    """Vende o publica en lote todas las armas de bajo valor de un usuario."""
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
    """Genera un informe integral del mercado y balance patrimonial de los usuarios."""
    total_ofertas_activas = len(mercado.ofertas_activas)
    valor_acumulado_activas = sum(o.precio for o in mercado.ofertas_activas)

    ventas_concluidas = [o for o in mercado.historial if o.estado == "Vendida"]
    ofertas_canceladas = [o for o in mercado.historial if o.estado == "Cancelada"]
    volumen_ventas = sum(o.precio for o in ventas_concluidas)

    oferta_mas_cara = max(ventas_concluidas, key=lambda o: o.precio) if ventas_concluidas else None

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

