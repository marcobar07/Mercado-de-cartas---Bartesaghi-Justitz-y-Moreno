Les pido dos cambios de diseño sobre lo que ya tienen.

1) Sacar el estado global
Hoy la semilla, el contador de IDs, el historial de eventos y las comisiones viven en variables de módulo (semilla.py y soporte_global.py). 
Además, gestionar_compra_oferta modifica una de ellas desde otro módulo. 
Pásenlo a objetos (por ejemplo Generador y Auditor) que se crean una vez y se entregan a quien los necesita. 
Objetivo: poder correr dos simulaciones a la vez sin que se pisen entre sí.

2) Calcular el valor del arma en un solo lugar
Hoy calcular_valor guarda self.valor, y cada subclase lo corrige después de que ya lo calculó la clase padre. 
Dejen la fórmula una sola vez en Arma, y que cada subclase solo aporte su propio dato (por ejemplo, su multiplicador).

Qué tienen que entregar
- UML del antes y del después.
- Un commit por cada cambio, con un mensaje que diga qué cambió y por qué.

Una ayuda extra, por haberme mandado el código a tiempo: hay un error escondido en ArmaBlanca.calcular_valor. 
Prueben crear dos cuchillos iguales, uno StatTrak y otro no, y comparen los valores. 
¿Cuál debería valer más? ¿Cuál vale más hoy? Pista: miren qué hace esa subclase con el multiplicador de StatTrak que la clase padre ya aplicó. 
Si hacen el cambio 2 bien hecho, el error desaparece solo.
