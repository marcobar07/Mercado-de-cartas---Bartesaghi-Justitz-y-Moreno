1) Datos que maneja la aplicación

Todos los datos viven en memoria mientras dura la ejecución. Tampoco pedimos nombre, correo ni edad. Es una decisión de minimización: lo que no se recolecta no se puede filtrar.

El dato central es cada usuario (Usuario.id). Aparece en Usuario, en cada Oferta y en los eventos del Auditor, y sirve para identificar al dueño de los fondos, las armas y las ofertas. No es un nombre real, pero la Ley 18.331 considera dato personal a la información sobre personas "determinadas o determinables", y un alias puede volver determinable a una persona. Por eso lo tratamos como un dato personal indirecto.

Junto al alias se guardan los fondos y el inventario de cada usuario. Por cada transacción  se guardan: el precio, el comprador y el vendedor. Son datos de la cuenta, en moneda ficticia, y su finalidad es ejecutar las operaciones y poder reconstruirlas después.

Los datos que más cuidado necesitan son los que se derivan de otros. Cada Oferta y cada evento del Auditor llevan la fecha y hora en que ocurrieron. Su finalidad es ordenar la auditoría, pero en conjunto revelan cuándo juega cada persona. Además, la frecuencia de los eventos AGREGAR_FONDOS y APERTURA_CAJA puede mostrar un patrón de juego compulsivo aunque la moneda sea ficticia. Ninguno de esos datos es sensible por sí solo, pero juntos permiten inferir información importante.

2) Riesgo ético concreto y transparencia de probabilidades

En 2018, la Comisión de Juego de Bélgica consideró juego de azar a las loot boxes pagas, incluidas las de Counter-Strike, porque hay una apuesta, el azar decide el resultado y se puede ganar o perder. Nuestras cajas tienen la misma estructura que las lootboxes del anteror juego mencionado.

Las probabilidades de cada caja existen en el código, pero el jugador no las ve. Cada caja define en su LOOTPOOL el peso de cada arma posible. En las tres cajas, un arma azul sale el 65 % de las veces, una violeta el 20 %, una rosada el 9 %, una roja el 4 % y un arma blanca (dorada) el 2 %. A eso se suman tres atributos aleatorios que también cambian el valor: el desgaste (entre 0 y 1), el patrón (entre 1 y 60) y la posibilidad de ser StatTrak (10 %). Nada de esto aparece en la tienda (accion_comprar_cajas): el jugador solo ve el nombre de la caja y su precio. Las probabilidades son transparentes para quien lee el código, no para quien paga.

Un punto a favor del diseño actual es que el azar es reproducible: toda la aleatoriedad pasa por un Generador con semilla. Con la misma semilla, cualquiera puede repetir una apertura y verificar que el resultado no fue manipulado. Es una forma de transparencia hacia quien audita el sistema, aunque todavía no hacia el jugador.

Para los jugadores que quieren conocer la probabilidad de conseguir cada arma y sus características, estan detalladas en el README.md.

Efecto sobre menores

La aplicación no verifica la edad y, por lo dicho en el punto 1, no debería pedirla. Aunque las probabilidades sean visibles y no haya ninguna forma de cargar dinero real, un menor que aprende que "abrir cajas es rentable" aprende la lógica de las apuestas.

3) Reglas inviolables y su verificación en pruebas unitarias

1. **El dinero no aparece ni desaparece en una transacción.** En toda compra entre usuarios, la suma de los fondos de los usuarios más el fondo de comisiones es igual antes y después. Solo hay dos excepciones explícitas: cargar saldo (entra dinero) y comprar una caja (sale dinero).
   - *Verificación en test:* `test_publicacion_y_compra_oferta_con_comision` (en `TestGestionMercadoFunciones`) y `test_dos_simulaciones_paralelas_no_se_pisan` (en `TestSimulacionesConcurrentesSinEstadoGlobal`), comprobando matemáticamente que la suma de saldos de comprador y vendedor previo a la compra sea idéntica a la suma posterior más la comisión retenida por el mercado.

2. **Ningún saldo es negativo, no se acepta ese estado.** Si una transacción resultaría en estado negativo, se rechaza.
   - *Verificación en test:* `test_validacion_fondos_y_gasto_no_negativo` (en `TestValidacionesYSeguridadTransaccional`), impidiendo saldos o gastos negativos con `ValueError`, junto con `test_compra_oferta_comprador_fondos_insuficientes` y `test_compra_y_apertura_caja_fondos_insuficientes` (en `TestCasosBordeYErrorGestionMercado`), que rechazan la compra si el usuario no posee fondos suficientes.

3. **Todo precio de oferta es positivo.**
   - *Verificación en test:* `test_precio_oferta_debe_ser_positivo` (en `TestValidacionesYSeguridadTransaccional`), comprobando que precios `<= 0` lanzan `ValueError` al instanciar `Oferta` o publicar en `Mercado`, y retornan `exito=False` en `gestionar_publicacion_oferta`.

4. **La comisión sobre las ventas es de 5%.**
   - *Verificación en test:* `test_publicacion_y_compra_oferta_con_comision` (en `TestGestionMercadoFunciones`) y `test_auditor_independiente_y_comisiones` (en `TestGeneradorYAuditor`), verificando que la retención aplicada sea exactamente `int(precio * 0.05)` y que la tasa predeterminada de `Auditor` sea `0.05`.

5. **Cada arma está en un solo lugar a la vez.** Está en un solo inventario o en una sola oferta activa, nunca en dos al mismo tiempo.
   - *Verificación en test:* `test_no_duplicar_arma_al_publicar_oferta` (al publicar, el arma sale del inventario y entra al mercado), `test_no_misma_arma_en_dos_inventarios` (prohíbe que dos usuarios tengan la misma arma lanzando `ValueError`) y `test_cancelacion_oferta_devuelve_arma` (el arma solo retorna al inventario una vez cancelada la oferta).

6. **Solo el dueño del arma puede publicarla en el mercado.**
   - *Verificación en test:* `test_no_duplicar_arma_al_publicar_oferta` (en `TestValidacionesYSeguridadTransaccional`), donde publicar un arma que no pertenece al usuario lanza `ValueError` en `Mercado.publicar_oferta` y retorna `exito=False` con motivo `"no posee el arma"` en `gestionar_publicacion_oferta`.

7. **Los ID de las armas son únicos dentro de una misma simulación.**
   - *Verificación en test:* `test_generadores_independientes` (en `TestGeneradorYAuditor`) y `test_dos_simulaciones_paralelas_no_se_pisan` (en `TestSimulacionesConcurrentesSinEstadoGlobal`), garantizando la secuencia autoincremental monótona de IDs únicos (`1001`, `1002`, etc.) mediante `Generador.generar_siguiente_id()`.

8. **No se puede comprar la oferta de uno mismo.**
   - *Verificación en test:* `test_prevenir_autocompra` (en `TestGestionMercadoFunciones`), donde si el comprador coincide con el vendedor de la oferta, la compra se aborta inmediatamente con `exito=False` y motivo `"propia oferta"`.

9. **Una oferta se cierra una sola vez.** Pasa de “En venta” a “Vendida” o a “Cancelada” y no vuelve atrás. Una oferta cerrada no se puede comprar ni cancelar.
   - *Verificación en test:* `test_transiciones_de_estado_oferta` (en `TestOfertaEstadosYMetodosDirectos`), `test_compra_oferta_inactiva_falla` (previene comprar ofertas ya cerradas o canceladas) y `test_cancelacion_oferta_ya_cancelada_falla` (previene cancelar una oferta ya cerrada).

10. **Solo el dueño de la oferta puede cancelarla.**
    - *Verificación en test:* `test_cancelacion_oferta_por_usuario_no_vendedor_falla` (en `TestCasosBordeYErrorGestionMercado`), rechazando con `exito=False` cualquier intento de cancelación realizado por un usuario distinto al vendedor original.

11. **Una operación inválida no deja rastros.** Si una operación compuesta falla a la mitad, el estado queda exactamente igual que antes (rollback).
    - *Verificación en test:* `test_rollback_falla_apertura_caja_no_deja_rastros` (en `TestValidacionesYSeguridadTransaccional`), comprobando que ante fallas durante la apertura de caja se reembolsan los fondos y se preserva el inventario sin saldos residuales ni ítems huérfanos.

12. **Con la misma semilla y los mismos datos, el resultado es siempre el mismo.**
    - *Verificación en test:* `test_reproducibilidad_con_misma_semilla` (en `TestSemillaYAleatoriedad`) y `test_generadores_independientes` (en `TestGeneradorYAuditor`), demostrando que fijar una misma semilla reproduce idénticamente todas las secuencias pseudoaleatorias, desgastes, patrones y StatTrak.

13. **Dos simulaciones no se afectan entre sí.**
    - *Verificación en test:* `test_dos_simulaciones_paralelas_no_se_pisan` (en `TestSimulacionesConcurrentesSinEstadoGlobal`), ejecutando dos simulaciones independientes en simultáneo con sus propios objetos `Generador`, `Auditor` y `Mercado`, demostrando que sus estados, inventarios, eventos y fondos jamás se cruzan.

14. **Las probabilidades que se muestran son las que se usan.**
    - *Verificación en test:* `test_abrir_caja_genera_arma_valida` (en `TestAperturaDeCajas`), `test_caja_suenos_y_pesadillas` y `test_caja_revolucion` (en `TestTodasLasCajasLootpool`) y `test_generador_metodos_atributos` (en `TestGeneradorYAuditorMetodosDetallados`), validando que las aperturas utilicen estrictamente los pesos de cada lootpool oficial, con desgaste en `[0.0, 1.0]`, patrón en `[1, 60]` y StatTrak en 10%.

15. **La moneda no tiene salida.** No existe ninguna operación que convierta fondos o armas en dinero real.
    - *Verificación en test:* `test_validacion_fondos_y_gasto_no_negativo` (en `TestValidacionesYSeguridadTransaccional`) y `test_gastar_fondos_cero` (en `TestUsuarioYMetodosAdicionales`), constatando que el modelo `Usuario` opera como un circuito financiero cerrado donde los únicos modificadores de saldo son `conseguir_fondos()` y `gastar_fondos()` dentro del juego, sin exponer interfaces de retiro o conversión a dinero real.
