Antes de ejecutar cada función clave anotamos qué esperamos que devuelva y por qué.
Después la ejecutamos y comparamos. 

 1. Valor de un arma ("Arma.calcular_valor")

    Ak47(1, "x", 0.10, 30, "roja", True).calcular_valor()

Predicción: 6840 aprox.
base de rareza roja (600) x StatTrak (1.5) x factor de desgaste ((2 − 0.10)³ / 2 = 3.4295)
x factor de patrón (1 + (30/50)³ / 2 = 1.108) x multiplicador de AK-47 (2.0) = 6839.8
Resultado: 6839
Comparación: acertamos

2. Cuchillo StatTrak contra cuchillo normal (`ArmaBlanca.calcular_valor`)

    st    = ArmaBlanca(1, "x", "Karambit", 0.10, 30, True).calcular_valor()
    no_st = ArmaBlanca(2, "x", "Karambit", 0.10, 30, False).calcular_valor()

Predicción:StatTrak = 11399 y sin StatTrak = 17099
Por qué: ArmaBlanca tiene stattrack_inverso = True, así que
calcular_multiplicador_stattrack() devuelve 1.0 si es StatTrak y 1.5 si no lo es.
Es al revés que en el resto de las armas, y es una decisión de diseño del grupo
(el StatTrak en cuchillos "se ve feo" y baja el precio). El cálculo es:
1000 x 1.0 x 3.4295 x 1.108 x 3.0 = 11399 contra 1000 x 1.5 x 3.4295 x 1.108 x 3.0 = 17099.
Resultado: StatTrak = 11399, sin StatTrak = 17099. El cuchillo sin StatTrak vale 1.5 veces más.
Comparación: acertamos (que el StatTrak valga menos es intencional, diferente de en armas normales)

3. Misma semilla, misma apertura (Caja.abrir)

    a = Kilovatio(1, Generador(7)).abrir(1, Generador(7))
    b = Kilovatio(1, Generador(7)).abrir(1, Generador(7))
    (a.skin, a.desgaste, a.patron, a.stattrack) == (b.skin, b.desgaste, b.patron, b.stattrack)

Predicción: las 2 aperturas daran igual
Resultado: Verdadero. Las dos aperturas dan Glock "Block-18", azul, desgaste 0.5021,
patrón 47, sin StatTrak.
Comparación: Si predecíamos un arma concreta, es casi seguro que no hubieramos acertamos cuál, pero si pudimos predecir que las dos serían iguales.

4. Gastar montos inválidos (Usuario.gastar_fondos)

    u = Usuario("u", 300)
    u.gastar_fondos(-100)
    u.gastar_fondos(500) 

Predicción: u.gastar_fondos(-100) lanzará value error por numero a gastar negativo y u.gastar_fondos(500) falso poruqe no hay saldo suficiente
Resultado: gastar_fondos(-100) lanza ValueError ("La cantidad a gastar debe ser un número
entero no negativo"). gastar_fondos(500) devuelve False, y u.fondos sigue en 300.
Comparación: nos dio bien

5. Publicar un arma ajena (Mercado.publicar_oferta)

    A = Usuario("A", 0); B = Usuario("B", 0)
    w = Glock(9, "g", 0.1, 10, "azul", False)
    B.agregar_arma(w)
    Mercado().publicar_oferta(A, w, 500)

Predicción: no se debería publicar
Resultado: lanza ValueError ("El vendedor 'A' no posee el arma 'g' (ID: 9) en su
inventario").
Comparación: antes de corregirlo esto duplicaba el arma, pero ahora funciona bien

6. Comisión sobre una venta barata (`gestionar_compra_oferta`)

    aud = Auditor()
    m = Mercado(aud)
    V = Usuario("V", 0)
    C = Usuario("C", 1000)
    w = Glock(10, "g", 0.1, 10, "azul", False)
    V.agregar_arma(w)
    r = f.gestionar_publicacion_oferta(m, V, w, precio_personalizado=19, auditor=aud)
    f.gestionar_compra_oferta(m, C, r["oferta"], auditor=aud)
    aud.obtener_fondos_comisiones(), V.fondos, C.fondos

Predicción: la comisión deberería ser 1
Por qué: la comisión se calcula como int(19 × 0.05) que es aprox 1
Resultado: comisión = 0, V.fondos = 19, C.fondos = 981
Comparación: le erramos, la comisión es 0 ya que int(trunca hacia abajo). Todas las ventas menores a 20 tendrán comisión 0.

8. Borrar un usuario (Simulacion.borrar_usuario)

    s = Simulacion("s", 42)
    s.crear_usuario("Ana", 1000)
    s.borrar_usuario("Ana")
    any("Ana" in e["descripcion"] for e in s.auditor.obtener_historial_eventos())

Predicción: Ana ya no esta en s.usuarios
Resultado: Verdadero, Ana ya no está en s.usuarios, pero su alias sigue en dos eventos del
Auditor: ALTA_USUARIO ("Se creó el usuario 'Ana' con saldo inicial $1,000") y
BAJA_USUARIO ("El usuario 'Ana' fue dado de baja...").
Comparación: acertamos
