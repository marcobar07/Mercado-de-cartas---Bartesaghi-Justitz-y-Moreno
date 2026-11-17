"""
Módulo del Menú Interactivo por Consola (CLI) para el Mercado de Cartas y Armas.
Permite gestionar múltiples simulaciones concurrentes e independientes,
usuarios, inventarios, compras, aperturas de cajas, publicaciones y compras en el mercado.
"""

from typing import Dict, List, Optional, Any
from creacion_de_clases import (
    Arma,
    ArmaBlanca,
    Ak47,
    AWP,
    Glock,
    RAREZAS,
    VALORES_RAREZA,
    Caja,
    Kilovatio,
    DreamsAndNightmares,
    Revolucion,
    Usuario,
    Oferta,
    Mercado,
    Generador,
    Auditor,
    Simulacion,
)
import funciones as f


# =====================================================================
# FUNCIONES AUXILIARES DE ENTRADA Y CONTROL DE CANCELACIÓN
# =====================================================================

def es_cancelar(texto: str) -> bool:
    """Detecta si el usuario desea cancelar la operación actual o volver."""
    return texto.strip().lower() in ("0", "cancelar", "cancel", "c")


def pedir_texto(prompt: str, permitir_vacio: bool = False) -> Optional[str]:
    """Solicita texto al usuario. Retorna None si ingresa 0 o 'cancelar'."""
    while True:
        try:
            entrada = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n>> Operación interrumpida.")
            return None
        if es_cancelar(entrada):
            print(">> Operación cancelada.")
            return None
        if not entrada and not permitir_vacio:
            print(">> Entrada vacía. Por favor ingrese un valor (o 0 / 'cancelar' para volver).")
            continue
        return entrada


def pedir_entero(prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
    """Solicita un entero. Retorna None si ingresa 0 o 'cancelar'."""
    while True:
        try:
            entrada = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n>> Operación interrumpida.")
            return None
        if es_cancelar(entrada):
            print(">> Operación cancelada.")
            return None
        try:
            val = int(entrada)
            if min_val is not None and val < min_val:
                print(f">> El número debe ser mayor o igual a {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f">> El número debe ser menor o igual a {max_val}.")
                continue
            return val
        except ValueError:
            print(">> Entrada inválida. Ingrese un número entero (o 0 / 'cancelar' para volver).")


def pedir_confirmacion(prompt: str) -> Optional[bool]:
    """Solicita confirmación afirmativa (s/n). Retorna None si cancela."""
    while True:
        try:
            entrada = input(f"{prompt} [s/n] (o 0 / 'cancelar'): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n>> Operación interrumpida.")
            return None
        if es_cancelar(entrada):
            print(">> Operación cancelada.")
            return None
        if entrada in ("s", "si", "sí", "y", "yes"):
            return True
        if entrada in ("n", "no"):
            return False
        print(">> Ingrese 's' para sí, 'n' para no (o 0 / 'cancelar' para volver).")


# =====================================================================
# FILTRADO AVANZADO DE OFERTAS EN EL MERCADO
# =====================================================================

def filtrar_ofertas(
    ofertas: List[Oferta],
    precio_min: Optional[int] = None,
    precio_max: Optional[int] = None,
    tipo_arma: Optional[str] = None,
    rareza: Optional[str] = None,
    skin: Optional[str] = None,
    stattrack: Optional[bool] = None,
    desgaste_min: Optional[float] = None,
    desgaste_max: Optional[float] = None,
    patron_min: Optional[int] = None,
    patron_max: Optional[int] = None,
) -> List[Oferta]:
    """Filtra una lista de ofertas activas según todos los criterios solicitados."""
    resultado = []
    for oferta in ofertas:
        arma = oferta.arma
        if precio_min is not None and oferta.precio < precio_min:
            continue
        if precio_max is not None and oferta.precio > precio_max:
            continue
        if tipo_arma is not None and tipo_arma.strip():
            filtro_t = tipo_arma.strip().lower()
            if filtro_t not in arma.tipo.lower() and filtro_t not in arma.__class__.__name__.lower():
                continue
        if rareza is not None and rareza.strip():
            if arma.rareza.lower() != rareza.strip().lower():
                continue
        if skin is not None and skin.strip():
            if skin.strip().lower() not in arma.skin.lower():
                continue
        if stattrack is not None:
            if arma.stattrack != stattrack:
                continue
        if desgaste_min is not None and arma.desgaste < desgaste_min:
            continue
        if desgaste_max is not None and arma.desgaste > desgaste_max:
            continue
        if patron_min is not None and arma.patron < patron_min:
            continue
        if patron_max is not None and arma.patron > patron_max:
            continue
        resultado.append(oferta)
    return resultado


def mostrar_tabla_ofertas(ofertas: List[Oferta]) -> None:
    """Muestra una lista de ofertas con formato tabular legible."""
    print("\n" + "=" * 115)
    print(f"{'#':<4} | {'Tipo':<12} | {'Skin':<18} | {'Rareza':<10} | {'Desgaste':<8} | {'Patrón':<6} | {'ST':<4} | {'Precio':<12} | {'Vendedor'}")
    print("-" * 115)
    for i, of in enumerate(ofertas, 1):
        arma = of.arma
        st_str = "Sí" if arma.stattrack else "No"
        print(f"[{i:<2}] | {arma.tipo:<12} | {arma.skin:<18} | {arma.rareza.capitalize():<10} | {arma.desgaste:<8.4f} | {arma.patron:<6} | {st_str:<4} | ${of.precio:<11,} | {of.vendedor.id}")
    print("=" * 115)


# =====================================================================
# ACCIONES ESPECÍFICAS DEL USUARIO
# =====================================================================

def accion_ver_armas(usuario: Usuario) -> None:
    """Muestra el inventario detallado de armas del usuario."""
    print("\n" + "=" * 80)
    print(f"=== INVENTARIO DE ARMAS DE {usuario.id} ===")
    print("=" * 80)
    if not usuario.inventario_armas:
        print(">> El usuario no posee armas en su inventario.")
    else:
        for i, arma in enumerate(usuario.inventario_armas, 1):
            st_str = "Sí" if arma.stattrack else "No"
            valor = arma.calcular_valor()
            print(f"[{i:<2}] ID: {arma.id:<4} | {arma.tipo:<12} ({arma.skin})")
            print(f"     Rareza: {arma.rareza.capitalize():<8} | Desgaste: {arma.desgaste:<6.4f} | Patrón: {arma.patron:<4} | StatTrak: {st_str:<3} | Valor: ${valor:,}")
        print("-" * 80)
        print(f"Total de armas: {len(usuario.inventario_armas)} | Valor total patrimonial: ${usuario.valor_inventario():,}")
    print("=" * 80)
    input("\nPresione ENTER para continuar...")


def accion_ver_cajas(usuario: Usuario) -> None:
    """Muestra el inventario de cajas del usuario."""
    print("\n" + "=" * 70)
    print(f"=== INVENTARIO DE CAJAS DE {usuario.id} ===")
    print("=" * 70)
    if not usuario.inventario_cajas:
        print(">> El usuario no posee cajas en su inventario.")
    else:
        for i, caja in enumerate(usuario.inventario_cajas, 1):
            print(f"[{i:<2}] ID Caja: {caja.id:<5} | {caja.nombre:<28} | Precio de compra: ${caja.precio:,}")
        print("-" * 70)
        print(f"Total de cajas disponibles: {len(usuario.inventario_cajas)}")
    print("=" * 70)
    input("\nPresione ENTER para continuar...")


def accion_comprar_cajas(sim: Simulacion, usuario: Usuario) -> None:
    """Permite al usuario adquirir cajas para su inventario."""
    catalogo = [
        ("Caja Kilovatio", Kilovatio, Kilovatio.PRECIO_FIJO),
        ("Caja Sueños y Pesadillas", DreamsAndNightmares, DreamsAndNightmares.PRECIO_FIJO),
        ("Caja Revolución", Revolucion, Revolucion.PRECIO_FIJO),
    ]

    while True:
        print("\n" + "=" * 60)
        print("=== TIENDA: COMPRA DE CAJAS ===")
        print("=" * 60)
        print(f"Saldo actual de {usuario.id}: ${usuario.fondos:,}\n")
        print("Catálogo disponible:")
        for idx, (nombre, _, precio) in enumerate(catalogo, 1):
            print(f"  [{idx}] {nombre:<28} - ${precio:,}")
        print("  [0] Cancelar / Volver")

        seleccion = pedir_texto("\nSeleccione la caja que desea comprar: ")
        if seleccion is None or seleccion == "0":
            return

        try:
            opcion = int(seleccion)
            if 1 <= opcion <= len(catalogo):
                nombre_caja, ClaseCaja, precio_unitario = catalogo[opcion - 1]

                cantidad = pedir_entero(f"¿Cuántas unidades de '{nombre_caja}' desea comprar? (o 0 / 'cancelar'): ", min_val=1)
                if cantidad is None:
                    return

                costo_total = precio_unitario * cantidad
                if usuario.fondos < costo_total:
                    print(f"\n>> [ERROR] Fondos insuficientes. Necesitas ${costo_total:,} y dispones de ${usuario.fondos:,}.")
                    input("\nPresione ENTER para continuar...")
                    continue

                confirma = pedir_confirmacion(f"¿Confirma la compra de {cantidad}x {nombre_caja} por un total de ${costo_total:,}?")
                if confirma:
                    usuario.gastar_fondos(costo_total)
                    for _ in range(cantidad):
                        sim.contador_cajas += 1
                        nueva_caja = ClaseCaja(id_caja=sim.contador_cajas, generador=sim.generador)
                        usuario.agregar_caja(nueva_caja)

                    sim.auditor.registrar_evento(
                        tipo="COMPRA_CAJA",
                        descripcion=f"{usuario.id} compró {cantidad}x {nombre_caja} por ${costo_total:,}.",
                        datos={"usuario": usuario.id, "caja": nombre_caja, "cantidad": cantidad, "costo": costo_total}
                    )
                    print(f"\n>> ¡Compra exitosa! Se añadieron {cantidad}x '{nombre_caja}' a tu inventario.")
                    print(f">> Saldo restante: ${usuario.fondos:,}")
                else:
                    print(">> Compra cancelada.")
                input("\nPresione ENTER para continuar...")
                return
            else:
                print(">> Opción fuera de rango.")
        except ValueError:
            print(">> Por favor ingrese un número válido.")


def accion_abrir_cajas(sim: Simulacion, usuario: Usuario) -> None:
    """Permite al usuario abrir una caja de su inventario."""
    if not usuario.inventario_cajas:
        print("\n>> No posees cajas en tu inventario para abrir. Compra cajas primero.")
        input("\nPresione ENTER para continuar...")
        return

    print("\n" + "=" * 70)
    print("=== APERTURA DE CAJAS ===")
    print("=" * 70)
    print("Selecciona qué caja de tu inventario deseas abrir:")
    for i, caja in enumerate(usuario.inventario_cajas, 1):
        print(f"  [{i}] ID: {caja.id:<5} | {caja.nombre:<28} (Costo original: ${caja.precio:,})")
    print("  [0] Cancelar / Volver")

    seleccion = pedir_texto("\nIngrese el número de la caja a abrir: ")
    if seleccion is None or seleccion == "0":
        return

    try:
        idx = int(seleccion)
        if 1 <= idx <= len(usuario.inventario_cajas):
            caja_elegida = usuario.inventario_cajas[idx - 1]
            id_nueva_arma = sim.generador.generar_siguiente_id()
            try:
                arma_obtenida = usuario.abrir_caja(caja_elegida, id_nueva_arma=id_nueva_arma, generador=sim.generador)
            except Exception as e:
                print(f">> [ERROR] Ocurrió un fallo al intentar abrir la caja: {e}")
                print(">> La caja no fue consumida y permanece en tu inventario.")
                input("\nPresione ENTER para continuar...")
                return

            if arma_obtenida is None:
                print(">> [ERROR] Ocurrió un fallo al intentar abrir la caja.")
                input("\nPresione ENTER para continuar...")
                return

            arma_obtenida.calcular_valor()
            rentabilidad = sim.auditor.evaluar_rentabilidad_apertura(caja_elegida.precio, arma_obtenida.valor)

            sim.auditor.registrar_evento(
                tipo="APERTURA_CAJA",
                descripcion=f"{usuario.id} abrió {caja_elegida.nombre} y obtuvo {arma_obtenida.tipo} ({arma_obtenida.skin}) valorada en ${arma_obtenida.valor:,}.",
                datos={
                    "usuario": usuario.id,
                    "caja": caja_elegida.nombre,
                    "arma_id": arma_obtenida.id,
                    "arma_tipo": arma_obtenida.tipo,
                    "skin": arma_obtenida.skin,
                    "valor": arma_obtenida.valor,
                    "rentabilidad": rentabilidad
                }
            )

            print("\n" + "=" * 60)
            print("=== ¡CAJA ABIERTA CON ÉXITO! ===")
            print("=" * 60)
            print(f"Caja consumida:    {caja_elegida.nombre} (Costo: ${caja_elegida.precio:,})")
            print(f"Arma obtenida:     {arma_obtenida.tipo} ({arma_obtenida.skin})")
            print(f"Rareza:            {arma_obtenida.rareza.capitalize()}")
            print(f"Desgaste:          {arma_obtenida.desgaste}")
            print(f"Patrón:            {arma_obtenida.patron}")
            print(f"StatTrak:          {'Sí' if arma_obtenida.stattrack else 'No'}")
            print(f"Valor cotizado:    ${arma_obtenida.valor:,}")
            print("-" * 60)
            print(f"Beneficio neto:    ${rentabilidad['beneficio_neto']:,}")
            print(f"ROI:               {rentabilidad['roi_porcentaje']}%")
            print(f"¿Rentable?:        {'SÍ' if rentabilidad['es_rentable'] else 'NO'}")
            print("=" * 60)
        else:
            print(">> Número de caja fuera de rango.")
    except ValueError:
        print(">> Entrada inválida.")

    input("\nPresione ENTER para continuar...")


def accion_publicar_oferta(sim: Simulacion, usuario: Usuario) -> None:
    """Permite al usuario poner a la venta un arma en el mercado."""
    if not usuario.inventario_armas:
        print("\n>> No posees armas en tu inventario para publicar.")
        input("\nPresione ENTER para continuar...")
        return

    print("\n" + "=" * 80)
    print("=== PUBLICAR OFERTA EN EL MERCADO ===")
    print("=" * 80)
    print("Selecciona el arma que deseas poner a la venta:")
    for i, arma in enumerate(usuario.inventario_armas, 1):
        st_str = "Sí" if arma.stattrack else "No"
        print(f"  [{i}] {arma.tipo:<12} ({arma.skin}) | Rareza: {arma.rareza.capitalize():<8} | StatTrak: {st_str:<3} | Valor: ${arma.calcular_valor():,}")
    print("  [0] Cancelar / Volver")

    seleccion = pedir_texto("\nIngrese el número del arma a publicar: ")
    if seleccion is None or seleccion == "0":
        return

    try:
        idx = int(seleccion)
        if 1 <= idx <= len(usuario.inventario_armas):
            arma_seleccionada = usuario.inventario_armas[idx - 1]
            valor_base = arma_seleccionada.calcular_valor()
            precio_sugerido = sim.auditor.calcular_precio_sugerido(valor_base, margen_porcentaje=0.10)

            print(f"\nArma elegida: {arma_seleccionada.tipo} ({arma_seleccionada.skin})")
            print(f"Valor base de cotización: ${valor_base:,}")
            print(f"Precio sugerido con margen (+10%): ${precio_sugerido:,}\n")

            print("¿Qué precio desea fijar para la oferta?")
            print(f"  [1] Usar precio sugerido (${precio_sugerido:,})")
            print("  [2] Ingresar un precio personalizado")
            print("  [0] Cancelar / Volver")

            opcion_precio = pedir_texto("\nSeleccione opción: ")
            if opcion_precio is None or opcion_precio == "0":
                return

            precio_final = None
            if opcion_precio == "1":
                precio_final = precio_sugerido
            elif opcion_precio == "2":
                precio_final = pedir_entero("Ingrese el precio personalizado deseado [$] (o 0 / 'cancelar'): ", min_val=1)
                if precio_final is None:
                    return
            else:
                print(">> Opción no válida.")
                input("\nPresione ENTER para continuar...")
                return

            res = f.gestionar_publicacion_oferta(
                mercado=sim.mercado,
                vendedor=usuario,
                arma=arma_seleccionada,
                precio_personalizado=precio_final,
                auditor=sim.auditor
            )

            if res["exito"]:
                print("\n" + "=" * 60)
                print("=== ¡OFERTA PUBLICADA CON ÉXITO! ===")
                print("=" * 60)
                print(f"Arma:              {arma_seleccionada.skin} ({arma_seleccionada.tipo})")
                print(f"Precio fijado:     ${precio_final:,}")
                print(f"Vendedor:          {usuario.id}")
                print(f"Ofertas activas:   {len(sim.mercado.ofertas_activas)}")
                print("=" * 60)
            else:
                print(f"\n>> No se pudo publicar la oferta: {res['motivo']}")
        else:
            print(">> Número de arma fuera de rango.")
    except ValueError:
        print(">> Entrada inválida.")

    input("\nPresione ENTER para continuar...")


def accion_buscar_ofertas(sim: Simulacion, usuario: Usuario) -> None:
    """
    Permite buscar ofertas en el mercado con filtros exhaustivos:
    - Rango de precios
    - Tipo de arma
    - Rareza
    - Skin específica
    - StatTrak
    - Rango de desgaste
    - Rango de patrón
    Y ofrece la posibilidad de comprar la oferta seleccionada.
    """
    print("\n" + "=" * 70)
    print("=== BÚSQUEDA Y COMPRA DE OFERTAS EN EL MERCADO ===")
    print("=" * 70)
    print(f"Usuario activo: {usuario.id} | Saldo disponible: ${usuario.fondos:,}")
    print(f"Total de ofertas activas en el mercado: {len(sim.mercado.ofertas_activas)}")

    if not sim.mercado.ofertas_activas:
        print("\n>> Actualmente no hay ninguna oferta activa en el mercado.")
        input("\nPresione ENTER para continuar...")
        return

    print("\nOpciones de búsqueda:")
    print("  [1] Ver todas las ofertas activas (sin filtros)")
    print("  [2] Aplicar filtros personalizados")
    print("  [0] Cancelar / Volver")

    opcion_busqueda = pedir_texto("\nSeleccione una opción: ")
    if opcion_busqueda is None or opcion_busqueda == "0":
        return

    ofertas_filtradas = list(sim.mercado.ofertas_activas)

    if opcion_busqueda == "2":
        print("\n--- CONFIGURACIÓN DE FILTROS ---")
        print("Presione ENTER en cualquier campo para omitir el filtro.")
        print("Puede escribir 0 o 'cancelar' en cualquier momento para abortar la búsqueda.\n")

        # 1. Rango de precios
        p_min_txt = pedir_texto("1. Precio mínimo [$] (ENTER para omitir): ", permitir_vacio=True)
        if p_min_txt is None: return
        p_min = int(p_min_txt) if p_min_txt.isdigit() else None

        p_max_txt = pedir_texto("2. Precio máximo [$] (ENTER para omitir): ", permitir_vacio=True)
        if p_max_txt is None: return
        p_max = int(p_max_txt) if p_max_txt.isdigit() else None

        # 2. Tipo de arma
        tipo_arma = pedir_texto("3. Tipo de arma (ej. Ak47, AWP, Glock, Kukri, etc.) (ENTER para omitir): ", permitir_vacio=True)
        if tipo_arma is None: return

        # 3. Rareza
        rareza = pedir_texto(f"4. Rareza ({', '.join(RAREZAS)}) (ENTER para omitir): ", permitir_vacio=True)
        if rareza is None: return

        # 4. Skin específica
        skin = pedir_texto("5. Skin o parte del nombre de la skin (ENTER para omitir): ", permitir_vacio=True)
        if skin is None: return

        # 5. StatTrak
        st_txt = pedir_texto("6. ¿Solo StatTrak? [s = Sí / n = No / ENTER = Ambos]: ", permitir_vacio=True)
        if st_txt is None: return
        st_val = None
        if st_txt.lower() in ("s", "si", "sí", "y", "1"):
            st_val = True
        elif st_txt.lower() in ("n", "no", "0"):
            st_val = False

        # 6. Rango de desgaste
        d_min_txt = pedir_texto("7. Desgaste mínimo (0.00 a 1.00) (ENTER para omitir): ", permitir_vacio=True)
        if d_min_txt is None: return
        try:
            d_min = float(d_min_txt.replace(",", ".")) if d_min_txt else None
        except ValueError:
            d_min = None

        d_max_txt = pedir_texto("8. Desgaste máximo (0.00 a 1.00) (ENTER para omitir): ", permitir_vacio=True)
        if d_max_txt is None: return
        try:
            d_max = float(d_max_txt.replace(",", ".")) if d_max_txt else None
        except ValueError:
            d_max = None

        # 7. Rango de patrón
        pat_min_txt = pedir_texto("9. Patrón mínimo (1 a 60) (ENTER para omitir): ", permitir_vacio=True)
        if pat_min_txt is None: return
        pat_min = int(pat_min_txt) if pat_min_txt.isdigit() else None

        pat_max_txt = pedir_texto("10. Patrón máximo (1 a 60) (ENTER para omitir): ", permitir_vacio=True)
        if pat_max_txt is None: return
        pat_max = int(pat_max_txt) if pat_max_txt.isdigit() else None

        ofertas_filtradas = filtrar_ofertas(
            ofertas=ofertas_filtradas,
            precio_min=p_min,
            precio_max=p_max,
            tipo_arma=tipo_arma if tipo_arma else None,
            rareza=rareza if rareza else None,
            skin=skin if skin else None,
            stattrack=st_val,
            desgaste_min=d_min,
            desgaste_max=d_max,
            patron_min=pat_min,
            patron_max=pat_max,
        )

    if not ofertas_filtradas:
        print("\n>> No se encontraron ofertas que coincidan con los criterios de búsqueda.")
        input("\nPresione ENTER para continuar...")
        return

    mostrar_tabla_ofertas(ofertas_filtradas)

    print(f"\nTu saldo disponible: ${usuario.fondos:,}")
    seleccion = pedir_texto("\nIngrese el número [#] de la oferta que desea comprar (o 0 / 'cancelar' para volver): ")
    if seleccion is None or seleccion == "0":
        return

    try:
        idx = int(seleccion)
        if 1 <= idx <= len(ofertas_filtradas):
            oferta_elegida = ofertas_filtradas[idx - 1]

            if oferta_elegida.vendedor.id == usuario.id:
                print("\n>> [ERROR] Un usuario no puede comprar su propia oferta.")
                input("\nPresione ENTER para continuar...")
                return

            if usuario.fondos < oferta_elegida.precio:
                print(f"\n>> [ERROR] Fondos insuficientes. La oferta cuesta ${oferta_elegida.precio:,} y tienes ${usuario.fondos:,}.")
                input("\nPresione ENTER para continuar...")
                return

            confirma = pedir_confirmacion(f"¿Desea comprar {oferta_elegida.arma.skin} a {oferta_elegida.vendedor.id} por ${oferta_elegida.precio:,}?")
            if confirma:
                res = f.gestionar_compra_oferta(
                    mercado=sim.mercado,
                    comprador=usuario,
                    oferta=oferta_elegida,
                    aplicar_comision=True,
                    auditor=sim.auditor
                )
                if res["exito"]:
                    print("\n" + "=" * 60)
                    print("=== ¡TRANSACCIÓN COMPLETADA! ===")
                    print("=" * 60)
                    print(f"Arma recibida:        {res['arma']}")
                    print(f"Vendedor:             {res['vendedor']}")
                    print(f"Precio pagado:        ${res['precio']:,}")
                    print(f"Comisión retenida:    ${res['comision_mercado']:,}")
                    print(f"Tu nuevo saldo:       ${usuario.fondos:,}")
                    print(f"Valor tu inventario:  ${usuario.valor_inventario():,}")
                    print("=" * 60)
                else:
                    print(f"\n>> Error en la transacción: {res['motivo']}")
            else:
                print(">> Compra cancelada.")
        else:
            print(">> Número de oferta fuera de rango.")
    except ValueError:
        print(">> Entrada inválida.")

    input("\nPresione ENTER para continuar...")


def accion_agregar_saldo(sim: Simulacion, usuario: Usuario) -> None:
    """Permite ingresar fondos a la cuenta del usuario."""
    print("\n" + "=" * 60)
    print("=== AGREGAR SALDO ===")
    print("=" * 60)
    print(f"Usuario: {usuario.id} | Saldo actual: ${usuario.fondos:,}")

    monto = pedir_entero("\nIngrese el monto a agregar [$] (o 0 / 'cancelar' para volver): ", min_val=1)
    if monto is None:
        return

    usuario.conseguir_fondos(monto)
    sim.auditor.registrar_evento(
        tipo="AGREGAR_FONDOS",
        descripcion=f"{usuario.id} agregó fondos por ${monto:,}. Saldo resultante: ${usuario.fondos:,}.",
        datos={"usuario": usuario.id, "monto_agregado": monto, "nuevo_saldo": usuario.fondos}
    )

    print("\n" + "=" * 60)
    print(f">> ¡Fondos acreditados con éxito!")
    print(f">> Monto acreditado: +${monto:,}")
    print(f">> Nuevo saldo de {usuario.id}: ${usuario.fondos:,}")
    print("=" * 60)
    input("\nPresione ENTER para continuar...")


# =====================================================================
# MENÚ DEL USUARIO SELECCIONADO
# =====================================================================

def menu_usuario(sim: Simulacion, usuario: Usuario) -> None:
    """Muestra el panel operativo para el usuario activo."""
    while True:
        print("\n" + "=" * 70)
        print(f"=== PANEL DE USUARIO: {usuario.id} (Simulación: {sim.nombre}) ===")
        print("=" * 70)
        print(f"💰 Saldo disponible:     ${usuario.fondos:,}")
        print(f"🔫 Armas en inventario:  {len(usuario.inventario_armas)} (Valor patrimonial: ${usuario.valor_inventario():,})")
        print(f"📦 Cajas en inventario:  {len(usuario.inventario_cajas)}")
        print("-" * 70)
        print("Operaciones disponibles:")
        print("  [1] Ver inventario de armas")
        print("  [2] Ver inventario de cajas")
        print("  [3] Comprar cajas")
        print("  [4] Abrir cajas")
        print("  [5] Publicar oferta en el mercado")
        print("  [6] Buscar ofertas en el mercado (filtrar y comprar)")
        print("  [7] Agregar saldo")
        print("  [0] Volver al menú de simulación (o escribir 'cancelar')")
        print("=" * 70)

        opcion = pedir_texto("Seleccione una opción: ")
        if opcion is None or opcion == "0":
            break

        if opcion == "1":
            accion_ver_armas(usuario)
        elif opcion == "2":
            accion_ver_cajas(usuario)
        elif opcion == "3":
            accion_comprar_cajas(sim, usuario)
        elif opcion == "4":
            accion_abrir_cajas(sim, usuario)
        elif opcion == "5":
            accion_publicar_oferta(sim, usuario)
        elif opcion == "6":
            accion_buscar_ofertas(sim, usuario)
        elif opcion == "7":
            accion_agregar_saldo(sim, usuario)
        else:
            print(">> Opción no reconocida. Intente nuevamente.")


# =====================================================================
# OPERACIONES DENTRO DE UNA SIMULACIÓN
# =====================================================================

def menu_crear_usuario(sim: Simulacion) -> None:
    """Solicita los datos y da de alta un nuevo usuario en la simulación."""
    print("\n" + "=" * 60)
    print(f"=== CREAR NUEVO USUARIO EN '{sim.nombre}' ===")
    print("=" * 60)

    id_usuario = pedir_texto("Ingrese el ID o nombre del nuevo usuario (o 0 / 'cancelar'): ")
    if id_usuario is None:
        return

    if id_usuario in sim.usuarios:
        print(f"\n>> [ERROR] Ya existe un usuario con el identificador '{id_usuario}'.")
        input("\nPresione ENTER para continuar...")
        return

    fondos = pedir_entero("Ingrese los fondos iniciales [$] (o 0 / 'cancelar' para volver): ", min_val=0)
    if fondos is None:
        return

    usuario_creado = sim.crear_usuario(id_usuario=id_usuario, fondos=fondos)
    print(f"\n>> ¡Usuario '{usuario_creado.id}' creado exitosamente con ${usuario_creado.fondos:,} de saldo inicial!")
    input("\nPresione ENTER para continuar...")


def menu_borrar_usuario(sim: Simulacion) -> None:
    """
    Da de baja un usuario:
    - Las pertenencias no se transfieren a nadie y se destruyen.
    - Las ofertas activas en el mercado se marcan como canceladas.
    """
    print("\n" + "=" * 70)
    print(f"=== DAR DE BAJA UN USUARIO EN '{sim.nombre}' ===")
    print("=" * 70)

    if not sim.usuarios:
        print(">> No hay usuarios registrados en esta simulación.")
        input("\nPresione ENTER para continuar...")
        return

    lista_usuarios = list(sim.usuarios.values())
    print("Usuarios actuales:")
    for i, u in enumerate(lista_usuarios, 1):
        print(f"  [{i}] ID: {u.id:<20} | Saldo: ${u.fondos:<10,} | Armas: {len(u.inventario_armas):<3} | Cajas: {len(u.inventario_cajas):<3}")
    print("  [0] Cancelar / Volver")

    seleccion = pedir_texto("\nIngrese el número del usuario a borrar: ")
    if seleccion is None or seleccion == "0":
        return

    try:
        idx = int(seleccion)
        if 1 <= idx <= len(lista_usuarios):
            usuario_a_borrar = lista_usuarios[idx - 1]
            ofertas_activas_cant = len([o for o in sim.mercado.ofertas_activas if o.vendedor.id == usuario_a_borrar.id])

            print("\n" + "!" * 70)
            print(f"ADVERTENCIA: Si da de baja al usuario '{usuario_a_borrar.id}':")
            print(f" - Sus pertenencias (${usuario_a_borrar.fondos:,} saldo, {len(usuario_a_borrar.inventario_armas)} armas, {len(usuario_a_borrar.inventario_cajas)} cajas) NO se transferirán a nadie.")
            print(f" - Sus {ofertas_activas_cant} oferta(s) activa(s) en el mercado serán canceladas.")
            print("!" * 70)

            confirma = pedir_confirmacion(f"¿Está seguro de que desea eliminar permanentemente al usuario '{usuario_a_borrar.id}'?")
            if confirma:
                sim.borrar_usuario(usuario_a_borrar.id)
                print(f"\n>> El usuario '{usuario_a_borrar.id}' ha sido dado de baja correctamente.")
            else:
                print(">> Operación cancelada.")
        else:
            print(">> Número fuera de rango.")
    except ValueError:
        print(">> Entrada inválida.")

    input("\nPresione ENTER para continuar...")


def menu_ver_historial(sim: Simulacion) -> None:
    """Muestra el historial completo de eventos registrados por la clase Auditor."""
    print("\n" + "=" * 90)
    print(f"=== HISTORIAL DE AUDITORÍA (AUDITOR) - SIMULACIÓN: {sim.nombre} ===")
    print("=" * 90)
    print(f"Fondos acumulados por comisiones de mercado: ${sim.auditor.obtener_fondos_comisiones():,}")
    eventos = sim.auditor.obtener_historial_eventos()
    print(f"Total de eventos registrados: {len(eventos)}\n")

    if not eventos:
        print(">> No hay eventos registrados aún en esta simulación.")
    else:
        print(f"{'#':<4} | {'Fecha y Hora':<19} | {'Tipo':<22} | {'Descripción'}")
        print("-" * 90)
        for i, ev in enumerate(eventos, 1):
            ts_str = ev["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{i:<2}] | {ts_str} | {ev['tipo']:<22} | {ev['descripcion']}")
    print("=" * 90)
    input("\nPresione ENTER para continuar...")


def menu_ver_informe_mercado(sim: Simulacion) -> None:
    """Muestra el informe integral financiero del mercado utilizando gestion_mercado."""
    print("\n" + "=" * 70)
    print(f"=== INFORME FINANCIERO DEL MERCADO - {sim.nombre} ===")
    print("=" * 70)
    informe = f.gestionar_informe_completo_mercado(
        mercado=sim.mercado,
        usuarios=list(sim.usuarios.values()),
        auditor=sim.auditor
    )
    print(f"Ofertas actualmente activas:           {informe['ofertas_activas']}")
    print(f"Valor monetario en venta activa:       ${informe['valor_en_venta_activa']:,}")
    print(f"Total de ventas concluidas:            {informe['total_ventas_concluidas']}")
    print(f"Total de ofertas canceladas:           {informe['total_canceladas']}")
    print(f"Volumen total transaccionado:          ${informe['volumen_total_transaccionado']:,}")
    print(f"Fondos acumulados por comisiones:      ${informe['fondos_comisiones_mercado']:,}")
    print(f"Total de eventos en auditor:           {informe['total_eventos_registrados']}")
    if informe["arma_mas_cara_vendida"]:
        print(f"Venta más costosa:                     {informe['arma_mas_cara_vendida']['skin']} por ${informe['arma_mas_cara_vendida']['precio']:,}")
    print("=" * 70)
    input("\nPresione ENTER para continuar...")


def menu_simulacion(sim: Simulacion) -> None:
    """Menú principal para operar sobre una simulación específica."""
    while True:
        print("\n" + "=" * 70)
        print(f"=== SIMULACIÓN ACTIVA: '{sim.nombre}' ===")
        print("=" * 70)
        print(f"🎲 Semilla generador:       {sim.generador.obtener_semilla()}")
        print(f"📋 Eventos en auditor:      {len(sim.auditor.obtener_historial_eventos())}")
        print(f"👥 Usuarios registrados:    {len(sim.usuarios)} ({', '.join(sim.usuarios.keys()) if sim.usuarios else 'Sin usuarios'})")
        print(f"🏪 Ofertas en mercado:      {len(sim.mercado.ofertas_activas)}")
        print("-" * 70)
        print("Opciones de la simulación:")
        print("  [1] Seleccionar un usuario para operar")
        print("  [2] Crear un nuevo usuario")
        print("  [3] Borrar un usuario (dar de baja y cancelar sus ofertas)")
        print("  [4] Ver historial de eventos (Auditor)")
        print("  [5] Ver informe financiero del mercado")
        print("  [0] Volver al menú de simulaciones (o escribir 'cancelar')")
        print("=" * 70)

        opcion = pedir_texto("Seleccione una opción: ")
        if opcion is None or opcion == "0":
            break

        if opcion == "1":
            if not sim.usuarios:
                print("\n>> No hay usuarios creados en esta simulación. Cree uno primero.")
                input("\nPresione ENTER para continuar...")
                continue

            lista_u = list(sim.usuarios.values())
            print("\nUsuarios disponibles:")
            for i, u in enumerate(lista_u, 1):
                print(f"  [{i}] {u.id:<20} | Saldo: ${u.fondos:<10,} | Armas: {len(u.inventario_armas):<2} | Cajas: {len(u.inventario_cajas):<2}")
            print("  [0] Cancelar / Volver")

            sel_u = pedir_texto("\nSeleccione el número del usuario con el que desea operar: ")
            if sel_u is None or sel_u == "0":
                continue

            try:
                idx_u = int(sel_u)
                if 1 <= idx_u <= len(lista_u):
                    usuario_elegido = lista_u[idx_u - 1]
                    menu_usuario(sim, usuario_elegido)
                else:
                    print(">> Número de usuario fuera de rango.")
            except ValueError:
                print(">> Entrada inválida.")

        elif opcion == "2":
            menu_crear_usuario(sim)
        elif opcion == "3":
            menu_borrar_usuario(sim)
        elif opcion == "4":
            menu_ver_historial(sim)
        elif opcion == "5":
            menu_ver_informe_mercado(sim)
        else:
            print(">> Opción no reconocida. Intente nuevamente.")


# =====================================================================
# GESTIÓN Y MENÚ PRINCIPAL DE SIMULACIONES
# =====================================================================

def crear_simulacion_por_defecto() -> Simulacion:
    """Crea una simulación inicial lista para usar con usuarios y armas de prueba."""
    sim = Simulacion(nombre="Simulación Principal", semilla=42)

    vendedor = sim.crear_usuario("Usuario_Vendedor", fondos=20000)
    comprador = sim.crear_usuario("Usuario_Comprador", fondos=60000)

    # Entregar cajas iniciales al vendedor
    caja1 = Kilovatio(id_caja=sim.generador.generar_siguiente_id(), generador=sim.generador)
    caja2 = Revolucion(id_caja=sim.generador.generar_siguiente_id(), generador=sim.generador)
    vendedor.agregar_caja(caja1)
    vendedor.agregar_caja(caja2)

    # Abrir una caja para que el vendedor tenga armas listas para publicar
    arma_dropeada = vendedor.abrir_caja(caja1, id_nueva_arma=sim.generador.generar_siguiente_id(), generador=sim.generador)
    if arma_dropeada:
        arma_dropeada.calcular_valor()
        sim.auditor.registrar_evento(
            tipo="APERTURA_CAJA",
            descripcion=f"{vendedor.id} abrió {caja1.nombre} y obtuvo {arma_dropeada.tipo} ({arma_dropeada.skin}) valorada en ${arma_dropeada.valor:,}."
        )

    return sim


def menu_crear_simulacion(simulaciones: Dict[str, Simulacion]) -> None:
    """Permite crear una nueva simulación con nombre y semilla propios."""
    print("\n" + "=" * 60)
    print("=== CREAR NUEVA SIMULACIÓN ===")
    print("=" * 60)

    nombre = pedir_texto("Ingrese el nombre de la nueva simulación (o 0 / 'cancelar'): ")
    if nombre is None:
        return

    if nombre in simulaciones:
        print(f"\n>> [ERROR] Ya existe una simulación llamada '{nombre}'.")
        input("\nPresione ENTER para continuar...")
        return

    semilla_txt = pedir_texto("Ingrese la semilla numérica para el Generador [Default: 42] (o 0 / 'cancelar'): ", permitir_vacio=True)
    if semilla_txt is None:
        return

    semilla = int(semilla_txt) if semilla_txt.isdigit() else 42
    nueva_sim = Simulacion(nombre=nombre, semilla=semilla)
    simulaciones[nombre] = nueva_sim

    print(f"\n>> ¡Simulación '{nombre}' creada exitosamente con semilla {semilla}!")
    input("\nPresione ENTER para continuar...")


def menu_borrar_simulacion(simulaciones: Dict[str, Simulacion]) -> None:
    """Permite eliminar una simulación existente."""
    print("\n" + "=" * 60)
    print("=== BORRAR SIMULACIÓN ===")
    print("=" * 60)

    if not simulaciones:
        print(">> No hay simulaciones disponibles para borrar.")
        input("\nPresione ENTER para continuar...")
        return

    nombres = list(simulaciones.keys())
    print("Simulaciones existentes:")
    for i, nombre in enumerate(nombres, 1):
        s = simulaciones[nombre]
        print(f"  [{i}] {nombre:<25} | Usuarios: {len(s.usuarios)} | Ofertas: {len(s.mercado.ofertas_activas)}")
    print("  [0] Cancelar / Volver")

    seleccion = pedir_texto("\nIngrese el número de la simulación que desea borrar: ")
    if seleccion is None or seleccion == "0":
        return

    try:
        idx = int(seleccion)
        if 1 <= idx <= len(nombres):
            nombre_a_borrar = nombres[idx - 1]
            confirma = pedir_confirmacion(f"¿Confirma la eliminación permanente de la simulación '{nombre_a_borrar}'?")
            if confirma:
                del simulaciones[nombre_a_borrar]
                print(f"\n>> Simulación '{nombre_a_borrar}' eliminada exitosamente.")
            else:
                print(">> Operación cancelada.")
        else:
            print(">> Número fuera de rango.")
    except ValueError:
        print(">> Entrada inválida.")

    input("\nPresione ENTER para continuar...")


def ejecutar_menu_principal() -> None:
    """Punto de entrada del menú por consola."""
    simulaciones: Dict[str, Simulacion] = {}
    sim_defecto = crear_simulacion_por_defecto()
    simulaciones[sim_defecto.nombre] = sim_defecto

    while True:
        print("\n" + "=" * 70)
        print("=== SISTEMA DE MERCADO DE ARMAS - SELECTOR DE SIMULACIONES ===")
        print("=" * 70)
        print("Simulaciones disponibles:")
        nombres = list(simulaciones.keys())
        if not nombres:
            print("  (No hay simulaciones creadas actualmente)")
        else:
            for i, nom in enumerate(nombres, 1):
                s = simulaciones[nom]
                print(f"  [{i}] {nom:<25} | Semilla: {s.generador.obtener_semilla():<10} | Usuarios: {len(s.usuarios):<2} | Ofertas: {len(s.mercado.ofertas_activas)}")

        print("-" * 70)
        print("Acciones disponibles:")
        print("  [1] Seleccionar una simulación para trabajar")
        print("  [2] Crear una nueva simulación")
        print("  [3] Borrar una simulación existente")
        print("  [0] Salir del programa (o escribir 'cancelar')")
        print("=" * 70)

        opcion = pedir_texto("Seleccione una opción: ")
        if opcion is None or opcion == "0":
            print("\n>> Gracias por utilizar el sistema de Mercado de Armas. ¡Hasta luego!\n")
            break

        if opcion == "1":
            if not simulaciones:
                print("\n>> No hay simulaciones creadas. Por favor cree una primero.")
                input("\nPresione ENTER para continuar...")
                continue

            print("\nSeleccione la simulación con la que desea operar:")
            for i, nom in enumerate(nombres, 1):
                print(f"  [{i}] {nom}")
            print("  [0] Cancelar / Volver")

            sel_s = pedir_texto("\nIngrese número de simulación: ")
            if sel_s is None or sel_s == "0":
                continue

            try:
                idx_s = int(sel_s)
                if 1 <= idx_s <= len(nombres):
                    sim_elegida = simulaciones[nombres[idx_s - 1]]
                    menu_simulacion(sim_elegida)
                else:
                    print(">> Número de simulación fuera de rango.")
            except ValueError:
                print(">> Entrada inválida.")

        elif opcion == "2":
            menu_crear_simulacion(simulaciones)
        elif opcion == "3":
            menu_borrar_simulacion(simulaciones)
        else:
            print(">> Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    ejecutar_menu_principal()
