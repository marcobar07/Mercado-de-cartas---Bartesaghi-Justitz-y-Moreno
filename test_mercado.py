"""
Suite de pruebas unitarias para el sistema de mercado, cajas, armas y funciones con semilla.
Ejecutar con: python -m unittest test_mercado.py
"""

import importlib
import unittest

import funciones as f

# Carga directa del paquete 'creación de clases'
clases_mod = __import__("creación de clases")
Usuario = clases_mod.Usuario
Mercado = clases_mod.Mercado
Kilovatio = clases_mod.Kilovatio
DreamsAndNightmares = clases_mod.DreamsAndNightmares
Revolucion = clases_mod.Revolucion
ArmaBlanca = clases_mod.ArmaBlanca
Ak47 = clases_mod.Ak47
AWP = clases_mod.AWP
Glock = clases_mod.Glock
VALORES_RAREZA = clases_mod.VALORES_RAREZA


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


if __name__ == "__main__":
    unittest.main()
