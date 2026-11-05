from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from math import log
import random
from typing import List, Optional, Dict, Any

# ==========================================
# 1. ENUM DE RAREZAS
# ==========================================

class Rareza(str, Enum):
    AZUL = "azul"
    VIOLETA = "violeta"
    ROSADA = "rosada"
    ROJA = "roja"
    DORADA = "dorada"


# ==========================================
# 2. CLASES DE ARMAS (Jerarquía y abstracción)
# ==========================================

class Arma(ABC):
    """Clase abstracta base para todas las armas."""
    def __init__(self, id_arma: int, skin: str, desgaste: float, patron: int, rareza: Rareza, stattrack: bool, tipo: Optional[str] = None):
        self.id = id_arma
        self.skin = skin
        self.tipo = tipo if tipo is not None else self.__class__.__name__
        self.desgaste = desgaste
        self.patron = patron
        self.rareza = Rareza(rareza)

        # Validación según el tipo de arma
        if self.__class__.__name__ == "ArmaBlanca":
            if self.rareza != Rareza.DORADA:
                raise ValueError("Para las armas blancas la rareza debe ser 'dorada'.")
        else:
            if self.rareza == Rareza.DORADA:
                raise ValueError("Las armas convencionales solo pueden ser: azul, violeta, rosada o roja.")

        self.stattrack = stattrack
        self.valor: Optional[int] = None

    def calcular_valor(self) -> int:
        """
        Calcula el valor del arma según su rareza, patrón, desgaste y si es StatTrak,
        guarda el resultado en self.valor y lo retorna.
        """
        # 1. Valor base según la Rareza:
        valores_rareza = {
            Rareza.AZUL: 100,       
            Rareza.VIOLETA: 150,   
            Rareza.ROSADA: 300,   
            Rareza.ROJA: 600,      
            Rareza.DORADA: 1000,    
        }
        base_rareza = valores_rareza[self.rareza]

        # 2. Multiplicador o bonificación por StatTrak:
        multiplicador_stattrack = 1.5 if self.stattrack else 1.0  

        # 3. Factor por desgaste (self.desgaste es un float entre 0.00 y 1.00):
        # queremos que armas con poco desgaste ganen mucho valor y armas con desgasate alto valgan poco
        factor_desgaste = ((2 - self.desgaste)**3)/2  

        # 4. Factor o bonificación por patrón (self.patron es un número entero):
        # el patrón será un numero de 1 a 60
        # queremos que la mayoría de valores del patrón no afecten mucho el valor del arma, pero que
        # que el valor crezca de manera exponencial con el patrón, está es la fórmula que más nos gustó probando en geogebra
        factor_patron = 1+((self.patron/50)**3)/2

        # 5. Fórmula final: combina las variables anteriores según tu diseño
        valor_calculado = int(base_rareza * multiplicador_stattrack * factor_desgaste * factor_patron)

        # Se almacena en self.valor y se retorna
        self.valor = valor_calculado
        return self.valor


class ArmaBlanca(Arma):
    def __init__(self, id_arma: int, skin: str, tipo: str, desgaste: float, patron: int, stattrack: bool, rareza: Rareza = Rareza.DORADA):
        super().__init__(id_arma, skin, desgaste, patron, rareza, stattrack, tipo=tipo)

    def calcular_valor(self) -> int:
        # Llama a la fórmula base de Arma y permite agregar un multiplicador por la clase
        # A diferencia del resto de armas, las armas blancas tienen un multiplicador de StatTrak inverso
        #primero llamamos a calcular_valor para obtener el valor base
        super().calcular_valor()
      
        multiplicador_stattrack = 1.5 if self.stattrack else 1.0 
        #debemos anular el multiplicador que se le aplicó en calcular.valor
        self.valor = int(self.valor / multiplicador_stattrack)  
        #luego multiplicamos el valor base por el multiplicador de StatTrak inverso
        multiplicador_inverso = 1.0 if self.stattrack else 1.5 
        self.valor = int(self.valor * 3 * multiplicador_inverso)
        return self.valor


class Ak47(Arma):

    def calcular_valor(self) -> int:
        # Llama a la fórmula base de Arma y permite agregar un multiplicador por la clase
        super().calcular_valor()
        self.valor = int(self.valor * 2)
        return self.valor



class AWP(Arma):
    def calcular_valor(self) -> int:
        # Llama a la fórmula base de Arma y permite agregar un multiplicador por la clase
        super().calcular_valor()
        self.valor = int(self.valor * 1.5)
        return self.valor


class Glock(Arma):
    def calcular_valor(self) -> int:
        # Llama a la fórmula base de Arma y permite agregar un multiplicador por la clase
        super().calcular_valor()
        self.valor = int(self.valor * 1.2)
        return self.valor


# ==========================================
# 3. CLASES DE CAJAS (Jerarquía y abstracción)
# ==========================================

class Caja(ABC):
    """Clase abstracta base para las cajas de loot."""
    def __init__(self, id_caja: int, nombre: str, lootpool: List[Dict[str, Any]], precio: int):
        self.id = id_caja
        self.nombre = nombre
        self.lootpool = lootpool
        self.precio = precio

    def abrir(self, id_nueva_arma: int) -> Arma:
        """
        Selecciona un ítem del lootpool según sus probabilidades,
        genera sus atributos aleatorios (desgaste, patrón, stattrack)
        y devuelve una nueva instancia del arma calculando su valor.
        """
        if not self.lootpool:
            raise ValueError(f"La caja '{self.nombre}' no tiene ítems en su lootpool.")

        # 1. Selección ponderada por probabilidad
        pesos = [item["probabilidad"] for item in self.lootpool]
        item_elegido = random.choices(self.lootpool, weights=pesos, k=1)[0]

        # 2. Generación de atributos aleatorios del drop
        desgaste = round(random.uniform(0.00, 1.00), 4)
        patron = random.randint(1, 1000)
        stattrack = random.random() < 0.10  # 10% de probabilidad de ser StatTrak

        # 3. Instanciación del arma según su clase
        ClaseArma = item_elegido["clase"]

        if ClaseArma is ArmaBlanca:
            arma = ClaseArma(
                id_arma=id_nueva_arma,
                skin=item_elegido["skin"],
                tipo=item_elegido.get("subtipo", "Cuchillo"),
                desgaste=desgaste,
                patron=patron,
                stattrack=stattrack
            )
        else:
            arma = ClaseArma(
                id_arma=id_nueva_arma,
                skin=item_elegido["skin"],
                desgaste=desgaste,
                patron=patron,
                rareza=item_elegido["rareza"],
                stattrack=stattrack
            )

        # 4. Cálculo de su valor monetario
        arma.calcular_valor()
        return arma


class Kilovatio(Caja):
    PRECIO_FIJO = 250
    LOOTPOOL: List[Dict[str, Any]] = [
        {"clase": Glock, "skin": "Block-18", "rareza": Rareza.AZUL, "probabilidad": 79.92, "subtipo": None},
        {"clase": Glock, "skin": "High Beam", "rareza": Rareza.VIOLETA, "probabilidad": 15.98, "subtipo": None},
        {"clase": AWP, "skin": "Capillary", "rareza": Rareza.ROSADA, "probabilidad": 3.20, "subtipo": None},
        {"clase": Ak47, "skin": "Inheritance", "rareza": Rareza.ROJA, "probabilidad": 0.32, "subtipo": None},
        {"clase": AWP, "skin": "Chrome Cannon", "rareza": Rareza.ROJA, "probabilidad": 0.32, "subtipo": None},
        {"clase": ArmaBlanca, "subtipo": "Kukri", "skin": "Fade", "rareza": Rareza.DORADA, "probabilidad": 0.13},
        {"clase": ArmaBlanca, "subtipo": "Kukri", "skin": "Slaughter", "rareza": Rareza.DORADA, "probabilidad": 0.13},
    ]

    def __init__(self, id_caja: int):
        super().__init__(
            id_caja=id_caja,
            nombre="Caja Kilovatio",
            lootpool=list(self.LOOTPOOL),
            precio=self.PRECIO_FIJO
        )


class DreamsAndNightmares(Caja):
    PRECIO_FIJO = 300
    LOOTPOOL: List[Dict[str, Any]] = [
        {"clase": Glock, "skin": "Clear Polymer", "rareza": Rareza.AZUL, "probabilidad": 79.92, "subtipo": None},
        {"clase": AWP, "skin": "Exoskeleton", "rareza": Rareza.VIOLETA, "probabilidad": 15.98, "subtipo": None},
        {"clase": Glock, "skin": "Snack Attack", "rareza": Rareza.ROSADA, "probabilidad": 3.20, "subtipo": None},
        {"clase": Ak47, "skin": "Nightwish", "rareza": Rareza.ROJA, "probabilidad": 0.64, "subtipo": None},
        {"clase": ArmaBlanca, "subtipo": "Mariposa", "skin": "Lore", "rareza": Rareza.DORADA, "probabilidad": 0.13},
        {"clase": ArmaBlanca, "subtipo": "Bowie", "skin": "Gamma Doppler", "rareza": Rareza.DORADA, "probabilidad": 0.13},
    ]

    def __init__(self, id_caja: int):
        super().__init__(
            id_caja=id_caja,
            nombre="Caja Sueños y Pesadillas",
            lootpool=list(self.LOOTPOOL),
            precio=self.PRECIO_FIJO
        )


class Revolucion(Caja):
    PRECIO_FIJO = 350
    LOOTPOOL: List[Dict[str, Any]] = [
        {"clase": Glock, "skin": "Winterized", "rareza": Rareza.AZUL, "probabilidad": 79.92, "subtipo": None},
        {"clase": Glock, "skin": "Umbral Hare", "rareza": Rareza.VIOLETA, "probabilidad": 15.98, "subtipo": None},
        {"clase": AWP, "skin": "Duality", "rareza": Rareza.ROSADA, "probabilidad": 3.20, "subtipo": None},
        {"clase": Ak47, "skin": "Head Shot", "rareza": Rareza.ROJA, "probabilidad": 0.64, "subtipo": None},
        {"clase": ArmaBlanca, "subtipo": "Karambit", "skin": "Doppler", "rareza": Rareza.DORADA, "probabilidad": 0.13},
        {"clase": ArmaBlanca, "subtipo": "Mariposa", "skin": "Tiger Tooth", "rareza": Rareza.DORADA, "probabilidad": 0.13},
    ]

    def __init__(self, id_caja: int):
        super().__init__(
            id_caja=id_caja,
            nombre="Caja Revolución",
            lootpool=list(self.LOOTPOOL),
            precio=self.PRECIO_FIJO
        )


# ==========================================
# 4. CLASE OFERTA
# ==========================================

class Oferta:
    """Representa una oferta de venta en el mercado."""
    def __init__(self, vendedor: 'Usuario', arma: Arma, precio: int):
        self.vendedor = vendedor
        self.arma = arma
        self.estado = "En venta"  # "En venta", "Vendida", "Cancelada"
        self.precio = precio
        self.fecha_publicacion = datetime.now()
        self.fecha_cierre: Optional[datetime] = None
        self.comprador: Optional['Usuario'] = None

    def marcar_como_vendida(self, comprador: 'Usuario') -> None:
        """Método simple para actualizar el estado de la oferta a vendida."""
        self.estado = "Vendida"
        self.comprador = comprador
        self.fecha_cierre = datetime.now()

    def cancelar(self) -> None:
        """Método simple para cancelar la oferta."""
        self.estado = "Cancelada"
        self.fecha_cierre = datetime.now()


# ==========================================
# 5. CLASE USUARIO
# ==========================================

class Usuario:
    """Representa a un usuario del sistema (comprador y vendedor)."""
    def __init__(self, id_usuario: str, fondos: int = 0):
        self.id = id_usuario
        self.fondos = fondos
        self.inventario_armas: List[Arma] = []
        self.inventario_cajas: List[Caja] = []

    def conseguir_fondos(self, cantidad: int) -> None:
        """Aumenta los fondos del usuario."""
        self.fondos += cantidad

    def gastar_fondos(self, cantidad: int) -> bool:
        """Disminuye los fondos si hay saldo suficiente."""
        if self.fondos >= cantidad:
            self.fondos -= cantidad
            return True
        return False

    def agregar_arma(self, arma: Arma) -> None:
        """Añade un arma al inventario."""
        self.inventario_armas.append(arma)

    def quitar_arma(self, arma: Arma) -> None:
        """Remueve un arma del inventario si existe."""
        if arma in self.inventario_armas:
            self.inventario_armas.remove(arma)

    def agregar_caja(self, caja: Caja) -> None:
        """Añade una caja al inventario."""
        self.inventario_cajas.append(caja)

    def abrir_caja(self, caja: Caja, id_nueva_arma: int) -> Optional[Arma]:
        """Abre una caja de su inventario, la consume y agrega el arma obtenida."""
        if caja in self.inventario_cajas:
            self.inventario_cajas.remove(caja)
            arma_obtenida = caja.abrir(id_nueva_arma)
            self.agregar_arma(arma_obtenida)
            return arma_obtenida
        return None

    def calcular_valor_arma(self, arma: Arma) -> int:
        """Método auxiliar simple para obtener el valor individual de un arma."""
        return arma.calcular_valor()

    def valor_inventario(self) -> int:
        """Suma el valor total de todas las armas del inventario."""
        total = 0
        for arma in self.inventario_armas:
            total += self.calcular_valor_arma(arma)
        return total


# ==========================================
# 6. CLASE MERCADO
# ==========================================

class Mercado:
    """Gestiona las ofertas activas y el historial de transacciones."""
    def __init__(self):
        self.ofertas_activas: List[Oferta] = []
        self.historial: List[Oferta] = []

    def publicar_oferta(self, vendedor: Usuario, arma: Arma, precio: int) -> Oferta:
        """Crea una oferta, la añade a activas y quita el arma del inventario del vendedor."""
        vendedor.quitar_arma(arma)
        nueva_oferta = Oferta(vendedor, arma, precio)
        self.ofertas_activas.append(nueva_oferta)
        return nueva_oferta

    def cancelar_oferta(self, oferta: Oferta) -> None:
        """Pasa una oferta de activas al historial como cancelada y devuelve el arma al vendedor."""
        if oferta in self.ofertas_activas:
            self.ofertas_activas.remove(oferta)
            oferta.cancelar()
            oferta.vendedor.agregar_arma(oferta.arma)
            self.historial.append(oferta)

    def comprar_oferta(self, oferta: Oferta, comprador: Usuario) -> bool:
        """Procesa la compra de una oferta entre usuario y vendedor."""
        if oferta not in self.ofertas_activas:
            return False
        
        # Validar fondos del comprador
        if not comprador.gastar_fondos(oferta.precio):
            return False

        # Transferir fondos al vendedor
        oferta.vendedor.conseguir_fondos(oferta.precio)

        # Entregar arma al comprador
        comprador.agregar_arma(oferta.arma)

        # Actualizar estado de la oferta y moverla al historial
        oferta.marcar_como_vendida(comprador)
        self.ofertas_activas.remove(oferta)
        self.historial.append(oferta)
        
        return True
