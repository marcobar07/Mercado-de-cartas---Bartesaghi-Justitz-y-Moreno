"""
Archivo principal de ejecución (main.py) del sistema Mercado de Cartas / Armas.
Importa las clases modularizadas desde el paquete 'creacion_de_clases'
y las funciones auxiliares de gestión y aleatoriedad desde 'funciones'.
"""

import funciones as funciones
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
)


def ejecutar_simulacion():
    """Ejecuta una simulación completa del ciclo de vida del mercado."""
    print("=================================================================")
    print("=== SIMULACIÓN DEL MERCADO GESTIONADO DESDE Funciones.py ===")
    print("=================================================================")
    print(f"Semilla inicial: {funciones.obtener_semilla()}")

    # 1. Instanciación del Mercado y Usuarios
    mercado = Mercado()
    vendedor = Usuario(id_usuario="Usuario_Vendedor", fondos=2000)
    comprador = Usuario(id_usuario="Usuario_Comprador", fondos=60000)

    # 2. Gestión de compra y apertura de caja usando Funciones
    print("\n--- 1. COMPRA Y APERTURA DE CAJA ---")
    caja_a_comprar = Kilovatio(id_caja=1)
    resultado_apertura = funciones.gestionar_compra_y_apertura_caja(vendedor, caja_a_comprar)

    if resultado_apertura["exito"]:
        arma_dropeada = resultado_apertura["arma"]
        rent = resultado_apertura["rentabilidad"]
        print(f"Drop obtenido por {vendedor.id}: {arma_dropeada.tipo} ({arma_dropeada.skin})")
        print(f"  Rareza: {arma_dropeada.rareza} | Desgaste: {arma_dropeada.desgaste} | Patrón: {arma_dropeada.patron} | StatTrak: {arma_dropeada.stattrack}")
        print(f"  Valor estimado: ${arma_dropeada.valor} | Costo caja: ${caja_a_comprar.precio}")
        print(f"  Beneficio neto: ${rent['beneficio_neto']} | ROI: {rent['roi_porcentaje']}%")

        # 3. Gestión de publicación en el mercado con precio sugerido (+10%)
        print("\n--- 2. PUBLICACIÓN DE OFERTA EN EL MERCADO ---")
        resultado_pub = funciones.gestionar_publicacion_oferta(
            mercado=mercado,
            vendedor=vendedor,
            arma=arma_dropeada,
            margen_sugerido=0.10
        )
        oferta_creada = resultado_pub["oferta"]
        print(f"Oferta publicada con éxito por ${resultado_pub['precio']} (valor base: ${resultado_pub['valor_base']})")
        print(f"Ofertas activas en mercado: {len(mercado.ofertas_activas)}")

        # 4. Búsqueda y filtrado de ofertas en el mercado
        print("\n--- 3. BÚSQUEDA Y FILTRADO EN EL MERCADO ---")
        ofertas_encontradas = funciones.gestionar_busqueda_y_filtrado(
            mercado=mercado,
            rareza=arma_dropeada.rareza,
            ordenar_por="precio"
        )
        print(f"Ofertas activas encontradas de rareza '{arma_dropeada.rareza}': {len(ofertas_encontradas)}")

        # 5. Gestión de compra de la oferta con retención de comisión
        print("\n--- 4. EJECUCIÓN DE COMPRA CON COMISIÓN DE MERCADO ---")
        resultado_compra = funciones.gestionar_compra_oferta(
            mercado=mercado,
            comprador=comprador,
            oferta=oferta_creada,
            aplicar_comision=True
        )
        print(f"Transacción exitosa: {resultado_compra['exito']}")
        print(f"  Precio pactado: ${resultado_compra['precio']}")
        print(f"  Comisión retenida para el mercado: ${resultado_compra['comision_mercado']}")
        print(f"  Saldo final vendedor: ${resultado_compra['saldo_vendedor']}")
        print(f"  Saldo final comprador: ${resultado_compra['saldo_comprador']}")
        print(f"  Valor total inventario comprador: ${resultado_compra['valor_inventario_comprador']}")

        # 6. Informe completo del mercado y auditoría global
        print("\n--- 5. INFORME FINANCIERO Y AUDITORÍA GLOBAL ---")
        informe = funciones.gestionar_informe_completo_mercado(mercado, usuarios=[vendedor, comprador])
        print(f"Ventas totales concluidas: {informe['total_ventas_concluidas']}")
        print(f"Volumen total transaccionado: ${informe['volumen_total_transaccionado']}")
        print(f"Fondos acumulados por comisiones de mercado: ${informe['fondos_comisiones_mercado']}")
        print(f"Total de eventos de auditoría registrados: {informe['total_eventos_registrados']}")
        print(f"Semilla actual al finalizar: {funciones.obtener_semilla()}")


if __name__ == "__main__":
    ejecutar_simulacion()
