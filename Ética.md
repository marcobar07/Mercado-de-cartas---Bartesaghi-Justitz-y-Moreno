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

3) Reglas inviolables

1. El dinero no aparece ni desaparece en una transacción.. En toda compra entre usuarios, la suma de los fondos de los usuarios más el fondo de comisiones es igual antes y después. Solo hay dos excepciones explícitas: cargar saldo (entra dinero) y comprar una caja (sale dinero).
2. Ningún saldo es negativo, no se acepta ese estado. Si una transacción resultaría en estado negaativo, se rechaza.
3. Todo precio de oferta es positivo.
4. La comisión sobre las ventas es de 5%.
5. Cada arma está en un solo lugar a la vez. Está en un solo inventario o en una sola oferta activa, nunca en dos al mismo tiempo.
6. Solo el dueño del arma puede publicarla en el mercado.
7. los id de las armas son únicos dentro de una misma simulación.
8. No se puede comprar la oferta de uno mismo.
9. Una oferta se cierra una sola vez. Pasa de “En venta” a “Vendida” o a “Cancelada” y no vuelve atrás. Una oferta cerrada no se puede comprar ni cancelar.
10. Solo el dueño de la oferta puede cancelarla.
11. Una operación inválida no deja rastros. Si una operación compuesta falla a la mitad, el estado queda exactamente igual que antes.
12. Con la misma semilla y los mismos datos, el resultado es siempre el mismo.
13. Dos simulaciones no se afectan entre sí.
14. Las probabilidades que se muestran son las que se usan.
15. La moneda no tiene salida. No existe ninguna operación que convierta fondos o armas en dinero real.
