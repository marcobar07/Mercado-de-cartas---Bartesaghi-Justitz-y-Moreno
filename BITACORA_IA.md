Durante este proyecto la IA se utilizó principalmente como herramienta para picar código y resolver errores, no para diseñar la lógica ni la estructura del sistema. Se utilizó principalmente el modelo Gemini 3.8 Flash en su versión media y otros modelos de claude y chatgpt cuando nos quedamos sin créditos en el primero.

Prompts principales:
(de los prompts del 1 y 2 perdimos los chats por lo que sólo podemos dar una descripción de lo que le pedimos)
1) Lo primero que se le pidió basándose en el UML generara la creación de clases. Esto nos devolvió un código muy complejo que hasta implementaba cosas que no queríamos. Por lo que decidimos volver a empezar y tirarle otro prompt, yendo pasito a pasito.

2) De ahí le pedimos que basándose en el UML inicial generara un template para la creación de clases, dejando las funciones y los atributos que no pudiera conocer de antemano (como los lootpool de las cajas) vacíos. También se le pidió que cada método que creara no haga más de una cosa a la vez, ya que después serían llamados desde otras funciones que sí realizan operaciones más complejas.

Esto sí nos devolvió lo que queríamos, simplemente las definiciones sin código ni funcionalidad compleja todavía.

El único problema de diseño que nos devolvió es que las rarezas estaban hechas con una clase de tipo enum, lo cual no entendemos mucho su funcionalidad de antemano entonces le pedimos que simplemente las guardara en un diccionario con sus valores respectivos.


3) Se le pidió ayuda para la implementación del lootpool y de abrir cajas.

Su solución fue parecido a lo que nosotros habíamos pensado (una lista de diccionarios con la información del arma y sus pesos) pero no sabíamos cómo implementar la aleatoriedad en abrir la caja utilizando los pesos.

El problema de diseño de esto es que utilizaba la librería random sin semilla, por lo que no se podría recrear una caja abierta por ejemplo si se corriera el programa dos veces (que lo pide la consigna y tiene que ver con programación funcional). Esto se corregirá más adelante con la clase generador.

4) Se le pidió que agregara la funcionalidad para comprar cajas de parte de los usuarios.

Aquí se equivocó al crear una función que calcula el valor estimado de cada caja en lugar de simplemente dejar una variable en cada subclase como queríamos nosotros.

5) Ahora sí se le pidió que corrigiera la aleatoriedad con el siguiente prompt:
"todo lo que haz hecho con la librería random, quiero que lo hagas con la utilización de semilla, esta semilla que se guarde y se modifique desde el documento funciones y se altere cada vez que se llama la función."

Creó el archivo funciiones.py que funcionaba como queríamos (aunque posteriormente esto fuera modificado por el cambio pedido por los docentes).

6) Se le pidió que "ahora agrega las funciones de que sí gestionan el mercado de verdad en el documento funciones. Que estas básicamente llamen a los métodos de cada clase, que estas funciones sí hagan más de una cosa a la vez y puedan depender de varias funciones globales"

Este es nuestro borde menos funcional del código ya que las funciones dependen de variables globales y realizan muchas cosas a la vez. Pero tiene sentido porque de alguna manera se tienen que implementar e unir las funcionalidaddes individuales de los métodos.

7) Se le pidió que separara las clases cada una en su archivo propio dentro de una carpeta creacion_de_clases y las funciones de gestión separadas por tipo en archivos propios. 

Esto no dió problema alguno pero si en todas los archivos importara la librería os y sys para verificar la ubicación de los archivos, lo que le pedimos que eliminara porque no era necesario.
Aquí también creó automaticamente un unitest y un archivo main.py que cargaba automáticamente una simulación básica. Esto lo mantuvimos anque no fue algo que necesariamente le pedimos ya que creímos que no hacía daño tenerlo.

8) Luego vinieron los cambios de diseñio sugeridos por los docentes, para cambiar la ubicación de cálculo de valor y realizarlo sólo en la clase padre armas se le dieron los siguientes prompts: "Calcular el valor del arma en un solo lugar. Hoy calcular_valor guarda self.valor, y cada subclase lo corrige después de que ya lo calculó la clase padre. Deja la fórmula una sola vez en Arma, y que cada subclase solo aporte su propio dato (por ejemplo, su multiplicador)." y "muy bien, pero ahora quiero que sólo en las ArmaBlanca el valor del arma sea inverso según el StatTrack, que si no es stattrack tenga su multiplicador_stattrack = 1.5 y si stattrack = true su multiplicador_stattrack = 1"

El primer prompt arregló el problema de cambiar la fórmula en cada subclase y añadió una variable multiplicador para cada subclase, aplicando esta en la fórmula. Pero esto eliminó lo que queremos que hiciera sobre el statrack de las armas blancas. Por lo que se le tiró el segundo prompt que arregló el tema creando una nueva variable y método para esto.

9) Para eliminar el estado global se le dió el siguiente prompt: 
"Quiero hacer un cambio, Sacar el estado global. Hoy la semilla, el contador de IDs, el historial de eventos y las comisiones viven en variables de módulo (semilla.py y soporte_global.py). Además, gestionar_compra_oferta modifica una de ellas desde otro módulo. Pásenlo a objetos (por ejemplo Generador y Auditor) que se crean una vez y se entregan a quien los necesita. Objetivo: poder correr dos simulaciones a la vez sin que se pisen entre sí.

crealo en un archivo aparte dentro de creacion de clases"

Lo devolvió bien pero nos generó problema el nombre de la carpeta de creacion_de_clases, antes llamada "creación de clases" lo cual tuvimos que corregir.

10) Se le pidió que generara el código para una nueva clase simulación. Que básicamente contiene sus propios usuarios, auditor y generador. De esta manera hacer más fácil correr dos simulaciones en simultáneo.

Lo pudo hacer sin problema.

11) Con todo esto hecho nos sólo faltaba crear el menú, se le dió un prompt con la idea de la navegación de los menús y la IA sólo tenía que crear el código, no la lógica de cómo se iba a navegar: 

"Ya casi terminamos, lo único que nos falta es crear el menú. Lo primero que se debería ver al ejecutar el código es la selección de simulación que se quiere trabajar (o si se quiere crear o borrar una), cada simulación tiene asociada una instancia de la clase generador, una instancia de la clase mercado y una instancia de la clase auditor. 
Una vez elegida se debe preguntar con qué usuario se quiere trabajar, (o si se quiere crear uno nuevo) o si se quiere ver el historial (utilizando la clase auditor). También debería estar la opción de borrar un usuario, es importante que si se elige dar de baja un usuario, sus pertenencias no se transfieren a nadie y sus ofertas que tiene en el mercado se marcan como canceladas. 
Una vez que se elige el usuario se debe mostrar su saldo y debe haber opciones para: Ver inventario de armas, ver inventario de cajas, comprar cajas, abrir cajas, publicar oferta en el mercado o buscar ofertas en el mercado (que puede filtrarse por rango de precios, por tipo de arma, por rareza, por skin específica, si es statrack, rango de desgaste y rango de patrón), una vez elegida la opción de buscar ofertas se debería tener la opción de comprarla, y la opción de agregar saldo. 
FINALMENTE, ES IMPORTANTE QUE EN CADA PASO, SI SE LE PIDE AL USUARIO INGRESAR DATOS, QUE TENGA LA OPCIÓN DE ESCRIBIR 0 O "cancelar" PARA VOLVER HACIA ATRAS Y CANCELAR LA OPERACIÓN.
Todo esto crealo en un nuevo archivo menu.py"

Acá no tuvo errores mayores con la visión que teníamos.

12) Finalmente había un par de errores de consistencia y reglas de negocio que no habíamos considerado todavía, se le pidió que los corrigiera y que actualizara el readme y el unittest. El prompt principal de la corrección de errores era: 

"Hay un par de errores que debemos corregir, que son los siguientes:
Duplicar un arma. Mercado.publicar_oferta no verifica que el arma sea del vendedor. Si no la tiene, quitar_arma simplemente no hace nada. Hice que A publicara un arma de B, que C la comprara y que A cobrara 500. Resultado: el arma quedó en el inventario de B y en el de C a la vez. Esto se valida en gestionar_publicacion_oferta, pero no en la clase, así que cualquiera que use Mercado directamente puede saltearse la validación.
Misma arma en dos inventarios. agregar_arma acepta la misma arma dos veces. Con eso, dos compradores distintos terminaron con el mismo objeto.
Monedas que aparecen de la nada. gastar_fondos(-1_000_000) suma un millón. fondos es un atributo público, así que u.fondos = 999999 también funciona.
Precio negativo. Publiqué un arma a -300 y la compré: el comprador quedó con +300 y el vendedor con -300 (saldo negativo).
Una falla a mitad de camino deja rastros. Si caja.abrir() lanza una excepción (por ejemplo, con el lootpool vacío), el usuario ya pagó y ya perdió la caja: sus fondos pasaron de 1000 a 600 y no recibió ningún arma. No hay ningún mecanismo para volver atrás.

PARA CORREGIR ESTO NO IMPORTES NINGUNA LIBRERÍA NUEVA"

