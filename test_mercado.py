"""
Suite de pruebas unitarias para el sistema de mercado, cajas, armas y funciones con semilla.
Ejecutar con: python -m unittest test_mercado.py
"""

import unittest

import funciones as f
from creacion_de_clases import (
    Usuario,
    Mercado,
    Kilovatio,
    DreamsAndNightmares,
    Revolucion,
    ArmaBlanca,
    Ak47,
    AWP,
    Glock,
    VALORES_RAREZA,
    Generador,
    Auditor,
)


class TestSemillaYAleatoriedad(unittest.TestCase):
    def setUp(self):
        f.modificar_semilla(42)

    def test_semilla_se_altera_en_cada_llamada(self):
        semilla_inicial = f.obtener_semilla()
        _ = f.uniform(0.0, 1.0)
        semilla_tras_uniform = f.obtener_semilla()
        self.assertNotEqual(semilla_inicial, semilla_tras_uniform)

        _ = f.randint(1, 100)
        semilla_tras_randint = f.obtener_semilla()
        self.assertNotEqual(semilla_tras_uniform, semilla_tras_randint)

        _ = f.choices(["a", "b", "c"], weights=[1, 1, 1])
        semilla_tras_choices = f.obtener_semilla()
        self.assertNotEqual(semilla_tras_randint, semilla_tras_choices)

    def test_reproducibilidad_con_misma_semilla(self):
        f.modificar_semilla(12345)
        v1 = f.uniform(0.0, 1.0)
        v2 = f.randint(1, 500)
        drop = f.determinar_stattrack(0.10)

        # Reiniciar a la misma semilla
        f.modificar_semilla(12345)
        self.assertEqual(f.uniform(0.0, 1.0), v1)
        self.assertEqual(f.randint(1, 500), v2)
        self.assertEqual(f.determinar_stattrack(0.10), drop)


class TestRarezasYArmas(unittest.TestCase):
    def test_rareza_invalida_lanza_error(self):
        with self.assertRaises(ValueError):
            Glock(id_arma=1, skin="Test", desgaste=0.1, patron=100, rareza="arcoiris", stattrack=False)

    def test_arma_blanca_solo_acepta_rareza_dorada(self):
        with self.assertRaises(ValueError):
            ArmaBlanca(id_arma=1, skin="Fade", tipo="Kukri", desgaste=0.1, patron=100, rareza="azul", stattrack=False)
        
        # Con dorada no debe lanzar error
        cuchillo = ArmaBlanca(id_arma=1, skin="Fade", tipo="Kukri", desgaste=0.1, patron=100, rareza="dorada", stattrack=False)
        self.assertEqual(cuchillo.rareza, "dorada")

    def test_arma_convencional_no_acepta_dorada(self):
        with self.assertRaises(ValueError):
            Ak47(id_arma=1, skin="Redline", desgaste=0.1, patron=100, rareza="dorada", stattrack=False)

    def test_calculo_valor_arma(self):
        ak = Ak47(id_arma=1, skin="Inheritance", desgaste=0.5, patron=50, rareza="roja", stattrack=False)
        valor = ak.calcular_valor()
        self.assertIsInstance(valor, int)
        self.assertGreater(valor, 0)
        self.assertEqual(ak.valor, valor)

    def test_multiplicadores_aportados_por_subclase(self):
        self.assertEqual(Ak47.multiplicador, 2.0)
        self.assertEqual(AWP.multiplicador, 1.5)
        self.assertEqual(Glock.multiplicador, 1.2)
        self.assertEqual(ArmaBlanca.multiplicador, 3.0)

    def test_formula_unificada_no_sobreescrita_en_subclases(self):
        # La fórmula reside únicamente en Arma; las subclases solo aportan datos (multiplicador)
        self.assertNotIn("calcular_valor", Ak47.__dict__)
        self.assertNotIn("calcular_valor", AWP.__dict__)
        self.assertNotIn("calcular_valor", Glock.__dict__)
        self.assertNotIn("calcular_valor", ArmaBlanca.__dict__)

    def test_stattrack_inverso_solo_en_arma_blanca(self):
        # ArmaBlanca: no stattrack => 1.5x, stattrack => 1.0x
        cuchillo_sin_stattrack = ArmaBlanca(id_arma=1, skin="Fade", tipo="Kukri", desgaste=0.1, patron=100, stattrack=False)
        cuchillo_con_stattrack = ArmaBlanca(id_arma=2, skin="Fade", tipo="Kukri", desgaste=0.1, patron=100, stattrack=True)
        valor_sin = cuchillo_sin_stattrack.calcular_valor()
        valor_con = cuchillo_con_stattrack.calcular_valor()
        self.assertGreater(valor_sin, valor_con)
        self.assertAlmostEqual(valor_sin / valor_con, 1.5, delta=0.01)

        # Arma convencional: no stattrack => 1.0x, stattrack => 1.5x
        ak_sin_stattrack = Ak47(id_arma=3, skin="Inheritance", desgaste=0.1, patron=100, rareza="roja", stattrack=False)
        ak_con_stattrack = Ak47(id_arma=4, skin="Inheritance", desgaste=0.1, patron=100, rareza="roja", stattrack=True)
        self.assertGreater(ak_con_stattrack.calcular_valor(), ak_sin_stattrack.calcular_valor())
        self.assertAlmostEqual(ak_con_stattrack.valor / ak_sin_stattrack.valor, 1.5, delta=0.01)


class TestAperturaDeCajas(unittest.TestCase):
    def setUp(self):
        f.modificar_semilla(999)

    def test_abrir_caja_genera_arma_valida(self):
        caja = Kilovatio(id_caja=1)
        arma = caja.abrir(id_nueva_arma=10)
        self.assertIsNotNone(arma)
        self.assertTrue(0.0 <= arma.desgaste <= 1.0)
        self.assertTrue(1 <= arma.patron <= 1000)
        self.assertIn(arma.rareza, VALORES_RAREZA)
        self.assertGreater(arma.valor, 0)


class TestGestionMercadoFunciones(unittest.TestCase):
    def setUp(self):
        f.modificar_semilla(555)
        f.limpiar_historial_eventos()
        self.mercado = Mercado()
        self.vendedor = Usuario(id_usuario="Vendedor_Test", fondos=50000)
        self.comprador = Usuario(id_usuario="Comprador_Test", fondos=10_000_000)

    def test_compra_y_apertura_caja(self):
        caja = Kilovatio(id_caja=1)
        fondos_antes = self.vendedor.fondos
        res = f.gestionar_compra_y_apertura_caja(self.vendedor, caja)
        
        self.assertTrue(res["exito"])
        self.assertEqual(self.vendedor.fondos, fondos_antes - caja.precio)
        self.assertEqual(len(self.vendedor.inventario_armas), 1)
        self.assertEqual(len(self.vendedor.inventario_cajas), 0)

    def test_publicacion_y_compra_oferta_con_comision(self):
        # 1. Comprar y abrir caja para obtener un arma
        caja = Kilovatio(id_caja=1)
        res_apertura = f.gestionar_compra_y_apertura_caja(self.vendedor, caja)
        arma = res_apertura["arma"]

        # 2. Publicar oferta con margen del 10%
        res_pub = f.gestionar_publicacion_oferta(self.mercado, self.vendedor, arma, margen_sugerido=0.10)
        self.assertTrue(res_pub["exito"])
        oferta = res_pub["oferta"]
        self.assertEqual(len(self.mercado.ofertas_activas), 1)
        self.assertNotIn(arma, self.vendedor.inventario_armas)

        # 3. Comprar la oferta
        saldo_vendedor_previo = self.vendedor.fondos
        saldo_comprador_previo = self.comprador.fondos
        precio_oferta = oferta.precio

        res_compra = f.gestionar_compra_oferta(self.mercado, self.comprador, oferta, aplicar_comision=True)
        self.assertTrue(res_compra["exito"])

        # Verificar saldos considerando el 5% de comisión
        comision_esperada = int(precio_oferta * 0.05)
        self.assertEqual(self.comprador.fondos, saldo_comprador_previo - precio_oferta)
        self.assertEqual(self.vendedor.fondos, saldo_vendedor_previo + precio_oferta - comision_esperada)
        self.assertIn(arma, self.comprador.inventario_armas)
        self.assertEqual(len(self.mercado.ofertas_activas), 0)
        self.assertEqual(len(self.mercado.historial), 1)

    def test_prevenir_autocompra(self):
        caja = Kilovatio(id_caja=1)
        res = f.gestionar_compra_y_apertura_caja(self.vendedor, caja)
        arma = res["arma"]
        res_pub = f.gestionar_publicacion_oferta(self.mercado, self.vendedor, arma, precio_personalizado=1000)
        oferta = res_pub["oferta"]

        # El mismo vendedor intenta comprar su oferta
        res_compra = f.gestionar_compra_oferta(self.mercado, self.vendedor, oferta)
        self.assertFalse(res_compra["exito"])
        self.assertIn("propia oferta", res_compra["motivo"])

    def test_cancelacion_oferta_devuelve_arma(self):
        caja = Kilovatio(id_caja=1)
        res = f.gestionar_compra_y_apertura_caja(self.vendedor, caja)
        arma = res["arma"]
        res_pub = f.gestionar_publicacion_oferta(self.mercado, self.vendedor, arma, precio_personalizado=2000)
        oferta = res_pub["oferta"]

        res_cancel = f.gestionar_cancelacion_oferta(self.mercado, self.vendedor, oferta)
        self.assertTrue(res_cancel["exito"])
        self.assertIn(arma, self.vendedor.inventario_armas)
        self.assertEqual(len(self.mercado.ofertas_activas), 0)
        self.assertEqual(oferta.estado, "Cancelada")


class TestGeneradorYAuditor(unittest.TestCase):
    def test_generadores_independientes(self):
        gen1 = Generador(semilla=100, contador_id_inicial=1000)
        gen2 = Generador(semilla=100, contador_id_inicial=2000)

        # Mismas semillas iniciales generan mismas secuencias independientemente
        val1 = gen1.uniform(0.0, 1.0)
        val2 = gen2.uniform(0.0, 1.0)
        self.assertEqual(val1, val2)

        # Alterar gen1 no afecta a gen2
        _ = gen1.randint(1, 100)
        _ = gen1.alterar_semilla()
        self.assertNotEqual(gen1.obtener_semilla(), gen2.obtener_semilla())

        # Contadores de IDs independientes
        id1 = gen1.generar_siguiente_id()
        id2 = gen2.generar_siguiente_id()
        self.assertEqual(id1, 1001)
        self.assertEqual(id2, 2001)

    def test_auditor_independiente_y_comisiones(self):
        aud1 = Auditor(tasa_comision_default=0.05)
        aud2 = Auditor(tasa_comision_default=0.10)

        aud1.registrar_evento("TEST", "Evento en auditor 1")
        aud1.acumular_comision(500)

        # aud1 tiene datos
        self.assertEqual(len(aud1.obtener_historial_eventos()), 1)
        self.assertEqual(aud1.obtener_fondos_comisiones(), 500)

        # aud2 no fue tocado
        self.assertEqual(len(aud2.obtener_historial_eventos()), 0)
        self.assertEqual(aud2.obtener_fondos_comisiones(), 0)

        # Tasas de comisiones independientes
        self.assertEqual(aud1.calcular_comision_mercado(1000), 50)
        self.assertEqual(aud2.calcular_comision_mercado(1000), 100)


class TestSimulacionesConcurrentesSinEstadoGlobal(unittest.TestCase):
    """
    Verifica que dos simulaciones con sus propios Generador y Auditor
    puedan ejecutarse de manera entrelazada sin interferir en absoluto.
    """
    def test_dos_simulaciones_paralelas_no_se_pisan(self):
        # Configuración Simulación A
        gen_a = Generador(semilla=111, contador_id_inicial=1000)
        aud_a = Auditor()
        mercado_a = Mercado(auditor=aud_a)
        vendedor_a = Usuario("Vendedor_A", fondos=10000)
        comprador_a = Usuario("Comprador_A", fondos=50000)

        # Configuración Simulación B
        gen_b = Generador(semilla=999, contador_id_inicial=5000)
        aud_b = Auditor()
        mercado_b = Mercado(auditor=aud_b)
        vendedor_b = Usuario("Vendedor_B", fondos=20000)
        comprador_b = Usuario("Comprador_B", fondos=70000)

        # Paso 1: Simulación A compra y abre caja
        caja_a = Kilovatio(id_caja=1, generador=gen_a)
        res_a1 = f.gestionar_compra_y_apertura_caja(vendedor_a, caja_a, generador=gen_a, auditor=aud_a)
        self.assertTrue(res_a1["exito"])
        arma_a = res_a1["arma"]
        self.assertEqual(arma_a.id, 1001)

        # Verificar que Simulación B no fue afectada
        self.assertEqual(gen_b.obtener_contador_id(), 5000)
        self.assertEqual(gen_b.obtener_semilla(), 999)
        self.assertEqual(len(aud_b.obtener_historial_eventos()), 0)
        self.assertEqual(aud_b.obtener_fondos_comisiones(), 0)

        # Paso 2: Simulación B compra y abre caja
        caja_b = Revolucion(id_caja=2, generador=gen_b)
        res_b1 = f.gestionar_compra_y_apertura_caja(vendedor_b, caja_b, generador=gen_b, auditor=aud_b)
        self.assertTrue(res_b1["exito"])
        arma_b = res_b1["arma"]
        self.assertEqual(arma_b.id, 5001)

        # Paso 3: Publicaciones cruzadas en sus respectivos mercados
        pub_a = f.gestionar_publicacion_oferta(mercado_a, vendedor_a, arma_a, precio_personalizado=1000, auditor=aud_a)
        pub_b = f.gestionar_publicacion_oferta(mercado_b, vendedor_b, arma_b, precio_personalizado=2500, auditor=aud_b)
        self.assertEqual(len(mercado_a.ofertas_activas), 1)
        self.assertEqual(len(mercado_b.ofertas_activas), 1)

        # Paso 4: Compras en sus respectivos mercados con cobro de comisión
        compra_a = f.gestionar_compra_oferta(mercado_a, comprador_a, pub_a["oferta"], aplicar_comision=True, auditor=aud_a)
        self.assertTrue(compra_a["exito"])
        self.assertEqual(aud_a.obtener_fondos_comisiones(), 50)  # 5% de 1000
        self.assertEqual(aud_b.obtener_fondos_comisiones(), 0)   # Aún 0 en B

        compra_b = f.gestionar_compra_oferta(mercado_b, comprador_b, pub_b["oferta"], aplicar_comision=True, auditor=aud_b)
        self.assertTrue(compra_b["exito"])
        self.assertEqual(aud_b.obtener_fondos_comisiones(), 125) # 5% de 2500
        self.assertEqual(aud_a.obtener_fondos_comisiones(), 50)  # Inalterado en A

        # Paso 5: Informes finales independientes
        info_a = f.gestionar_informe_completo_mercado(mercado_a, usuarios=[vendedor_a, comprador_a], auditor=aud_a)
        info_b = f.gestionar_informe_completo_mercado(mercado_b, usuarios=[vendedor_b, comprador_b], auditor=aud_b)

        self.assertEqual(info_a["volumen_total_transaccionado"], 1000)
        self.assertEqual(info_b["volumen_total_transaccionado"], 2500)
        self.assertEqual(info_a["fondos_comisiones_mercado"], 50)
        self.assertEqual(info_b["fondos_comisiones_mercado"], 125)

        # Los historiales no se mezclaron
        for ev in aud_a.obtener_historial_eventos():
            self.assertNotIn("Vendedor_B", ev["descripcion"])
            self.assertNotIn("Comprador_B", ev["descripcion"])
        for ev in aud_b.obtener_historial_eventos():
            self.assertNotIn("Vendedor_A", ev["descripcion"])
            self.assertNotIn("Comprador_A", ev["descripcion"])


if __name__ == "__main__":
    unittest.main()
