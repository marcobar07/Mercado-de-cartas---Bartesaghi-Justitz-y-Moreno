# Mercado de Armas y Cajas (Skins)

**Proyecto Final de Programación Orientada a Objetos**  
*Autores: Bartesaghi, Justitz y Moreno*

---

## 📌 Descripción General

El proyecto simula un ecosistema completo de economía y mercado de armas y cajas de loot (inspirado en juegos como Counter-Strike). Permite a los usuarios:
1. **Administrar saldos y billeteras virtuales**.
2. **Comprar y abrir cajas de botín** (`Kilovatio`, `Sueños y Pesadillas`, `Revolución`).
3. **Obtener armas con atributos dinámicos** (rareza, desgaste, patrón numérico y tecnología StatTrak).
4. **Cotizar y calcular el valor monetario de las armas** mediante fórmulas matemáticas deterministas unificadas en la clase base `Arma`.
5. **Comerciar en un mercado centralizado** con publicación de ofertas, retención de comisiones (5%), cancelación y auditoría de transacciones.
6. **Ejecutar múltiples simulaciones independientes y concurrentes** sin colisión de estado, gracias a las clases `Generador`, `Auditor`, `Mercado` y `Simulacion`.
7. **Controlar la aleatoriedad** mediante un generador pseudoaleatorio basado en semillas reproducibles y auto-mutables encapsulado por simulación.
8. **Interactuar mediante un menú por consola (CLI)** completo e interactivo con soporte de cancelación global (`0` o `"cancelar"`).

---

## 📂 Estructura del Proyecto

```text
Mercado-de-cartas---Bartesaghi-Justitz-y-Moreno/
│
├── creacion_de_clases/
│   ├── __init__.py                  # Paquete que exporta todas las entidades
│   ├── clases_arma.py               # Jerarquía de Armas (Arma, Ak47, AWP, Glock, ArmaBlanca) y Rarezas
│   ├── clases_caja.py               # Jerarquía de Cajas de Loot (Caja, Kilovatio, DreamsAndNightmares, Revolucion)
│   ├── clase_usuarios.py            # Clase Usuario (billetera, inventarios de armas y cajas)
│   ├── clases_oferta_mercado.py     # Clases Oferta y Mercado
│   ├── clases_soporte.py            # Clases Generador y Auditor (estado y auditoría aislados)
│   └── clase_simulacion.py          # Clase Simulacion (instancia aislada con Generador, Auditor, Mercado y Usuarios)
│
├── funciones/
│   ├── __init__.py                  # Paquete que exporta las funciones auxiliares de gestión
│   ├── semilla.py                   # Funciones auxiliares de compatibilidad para semilla global
│   ├── soporte_global.py            # Funciones auxiliares de compatibilidad para soporte y auditoría global
│   └── gestion_mercado.py           # Orquestación de compras, ventas, aperturas y reportes
│
├── menu.py                          # Menú interactivo por consola (CLI) y punto de entrada principal
├── test_mercado.py                  # Suite de pruebas unitarias automáticas (17 tests)
├── UML inicial proyecto - Antes de cambios de diseño.drawio
├── UML proyecto - Después de cambios de diseño.drawio
└── .gitignore                       # Filtro de archivos temporales y compilados
```

---

## 🏗️ Arquitectura de Clases

### 1. Jerarquía de Armas (`clases_arma.py`)
- **`Arma` (ABC)**: Clase abstracta base.
  - **Atributos de instancia**: `id`, `skin`, `tipo`, `desgaste` (float 0.00-1.00), `patron` (entero 1-60), `rareza` (azul, violeta, rosada, roja, dorada), `stattrack` (booleano), `valor` (entero).
  - **Atributos de clase**: `multiplicador: float = 1.0`, `stattrack_inverso: bool = False`.
  - **Método unificado**: `calcular_valor() -> int`. La fórmula completa reside **exclusivamente en `Arma`**, calculando `self.valor` una sola vez. Ninguna subclase sobreescribe este método.
- **Subclases (aportan exclusivamente sus propios datos)**:
  - `Glock`: `multiplicador = 1.2`
  - `AWP`: `multiplicador = 1.5`
  - `Ak47`: `multiplicador = 2.0`
  - `ArmaBlanca`: `multiplicador = 3.0`, `stattrack_inverso = True` (exclusiva rareza dorada; multiplicador de StatTrak inverso: x1.5 si no es StatTrak, x1.0 si es StatTrak).

### 2. Rarezas y Valores Base
Las rarezas se definen mediante estructuras nativas:
- `RAREZAS`: `["azul", "violeta", "rosada", "roja", "dorada"]`
- `VALORES_RAREZA`:
  - `"azul"`: $100
  - `"violeta"`: $150
  - `"rosada"`: $300
  - `"roja"`: $600
  - `"dorada"`: $1000

### 3. Jerarquía de Cajas (`clases_caja.py`)
- **`Caja` (ABC)**:
  - Atributos: `id`, `nombre`, `lootpool`, `precio`, `generador`.
  - Método: `abrir(id_nueva_arma, generador) -> Arma` (consume números pseudoaleatorios del Generador asignado).
- **Cajas concretas**:
  - `Kilovatio` ($400)
  - `DreamsAndNightmares` ($500)
  - `Revolucion` ($450)

### 4. Usuario y Mercado (`clase_usuarios.py`, `clases_oferta_mercado.py`)
- **`Usuario`**:
  - Control de fondos (`conseguir_fondos`, `gastar_fondos`).
  - Inventario de armas y cajas (`agregar_arma`, `quitar_arma`, `agregar_caja`, `abrir_caja`, `valor_inventario`).
- **`Oferta`**:
  - Publicación en el mercado con estados: `"En venta"`, `"Vendida"`, `"Cancelada"`.
- **`Mercado`**:
  - Vinculado a su propio `Auditor`.
  - `publicar_oferta(vendedor, arma, precio)`
  - `cancelar_oferta(oferta)`
  - `comprar_oferta(oferta, comprador)`

### 5. Soporte y Simulación (`clases_soporte.py`, `clase_simulacion.py`)
- **`Generador`**:
  - Encapsula el estado pseudoaleatorio con una instancia aislada de `random.Random(semilla)`.
  - Generación de números aleatorios (`choices`, `uniform`, `randint`, `random_float`) con mutación automática y reproducible de la semilla.
  - Contador autoincremental de identificadores únicos de armas (`contador_id_armas`).
- **`Auditor`**:
  - Registro cronológico de eventos (`registrar_evento`, `obtener_historial_eventos`).
  - Fondos acumulados por comisión del mercado (`acumular_comision`, `obtener_fondos_comisiones`).
  - Cálculos financieros auxiliares (precios sugeridos con margen y evaluación de rentabilidad/ROI de cajas).
- **`Simulacion`**:
  - Integra en un único objeto contenedor: `Generador`, `Auditor`, `Mercado` y el registro de `Usuarios`.
  - Permite la creación y baja de usuarios.
  - **Regla de baja de usuario**: si se da de baja un usuario, sus pertenencias (saldo, armas y cajas) **no se transfieren a nadie y se destruyen**, y todas sus ofertas activas en el mercado se marcan como canceladas.

---

## 🎮 Menú Interactivo por Consola (`menu.py`)

El punto de entrada principal del sistema es `menu.py`, una interfaz por consola (CLI) intuitiva estructurada en tres niveles:

### 1. Nivel Superior: Selector de Simulaciones
- Permite seleccionar la simulación activa para operar.
- Permite **crear nuevas simulaciones** (con nombre y semilla personalizados).
- Permite **borrar simulaciones** (eliminando su mercado, generador y auditor asociados).

### 2. Nivel Intermedio: Panel de Simulación y Gestión de Usuarios
- **Seleccionar usuario activo** para operar.
- **Crear nuevo usuario** con saldo inicial.
- **Borrar usuario (Dar de baja)** con cancelación de ofertas activas y destrucción de pertenencias.
- **Ver historial de eventos** utilizando la clase `Auditor`.
- **Ver informe financiero completo** del mercado (volumen transaccionado, comisión acumulada, etc.).

### 3. Nivel Inferior: Panel Operativo del Usuario
Al seleccionar un usuario, se muestra su saldo y valor patrimonial junto a 7 opciones:
1. **Ver inventario de armas**: Detalle de IDs, skins, rareza, desgaste, patrón, StatTrak y valor cotizado.
2. **Ver inventario de cajas**: Cajas en posesión del usuario.
3. **Comprar cajas**: Catálogo de la tienda con selección de cantidad y validación de fondos.
4. **Abrir cajas**: Consume una caja del inventario y muestra un desglose con el arma obtenida, rentabilidad y ROI.
5. **Publicar oferta en el mercado**: Selección de arma con cotización base y precio sugerido (+10%) o personalizado.
6. **Buscar ofertas en el mercado**:
   - Filtrado avanzado por: rango de precios, tipo de arma, rareza, skin específica, StatTrak, rango de desgaste (0.00-1.00) y rango de patrón (1-1000).
   - Opción de **compra inmediata** de cualquier oferta encontrada, con retención de comisión y transferencia al comprador.
7. **Agregar saldo**: Acreditación directa de fondos registrada en el auditor.

> [!IMPORTANT]
> **Cancelación universal**: En **cada paso** donde se solicita ingreso de datos al usuario, es posible escribir **`0`** o **`"cancelar"`** para abortar la acción y regresar limpiamente al menú anterior sin modificar el estado.

---

## 🚀 Ejecución y Pruebas

### 1. Iniciar el Sistema Interactivo (Menú CLI)
```bash
python menu.py
```

### 2. Ejecutar la Suite de Pruebas Unitarias
Para correr las pruebas automatizadas:
```bash
python -m unittest test_mercado.py
```
*(17 pruebas unitarias completas que cubren: determinismo y mutación de semilla, validaciones de rarezas, cálculo unificado de valor de armas, multiplicador inverso de armas blancas, apertura de cajas, gestión de mercado, compras, cancelaciones, retención de comisiones y aislamiento entre múltiples simulaciones concurrentes).*
