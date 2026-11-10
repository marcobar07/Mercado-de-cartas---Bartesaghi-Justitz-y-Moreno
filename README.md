# Mercado de Armas y Cajas (Skins)

**Proyecto Final de Programación Orientada a Objetos**  
*Autores: Bartesaghi, Justitz y Moreno*

---

## 📌 Descripción General

El proyecto simula un ecosistema completo de economía y mercado de armas y cajas de loot (inspirado en juegos como Counter-Strike). Permite a los usuarios:
1. Administrar saldos y billeteras virtuales.
2. Comprar y abrir cajas de botín (`Kilovatio`, `Sueños y Pesadillas`, `Revolución`).
3. Obtener armas con atributos dinámicos (rareza, desgaste, patrón numérico y tecnología StatTrak).
4. Cotizar y calcular el valor monetario de las armas mediante fórmulas matemáticas deterministas.
5. Comerciar en un mercado centralizado con publicación de ofertas, retención de comisiones y auditoría de transacciones.
6. Controlar la aleatoriedad mediante un generador pseudoaleatorio basado en **semillas reproducibles y auto-mutables**.

---

## 📂 Estructura del Proyecto

```text
Mercado-de-cartas---Bartesaghi-Justitz-y-Moreno/
│
├── creación de clases/
│   ├── __init__.py                  # Paquete que exporta todas las entidades
│   ├── clases_arma.py               # Jerarquía de Armas y Rarezas (lista y diccionario)
│   ├── clases_caja.py               # Jerarquía de Cajas de Loot
│   ├── clase_usuarios.py            # Clase Usuario (billetera e inventarios)
│   └── clases_oferta_mercado.py     # Clases Oferta y Mercado
│
├── Funciones.py                     # Gestión de semilla, funciones pseudoaleatorias y orquestación
├── main.py                          # Punto de entrada y simulación principal
├── Creacion de clases proyecto final.py # Compatibilidad retroactiva
├── test_mercado.py                  # Suite de pruebas unitarias automáticas
├── Proyecto Final.drawio            # Diagramas de clases y arquitectura
└── .gitignore                       # Filtro de archivos compilados y temporales
```

---

## 🏗️ Arquitectura de Clases

### 1. Jerarquía de Armas (`clases_arma.py`)
- **`Arma` (ABC)**: Clase abstracta base.
  - Atributos: `id`, `skin`, `tipo`, `desgaste` (float 0.00-1.00), `patron` (entero 1-1000), `rareza` (azul, violeta, rosada, roja, dorada), `stattrack` (booleano), `valor` (entero).
  - Método: `calcular_valor() -> int`.
- **Subclases con multiplicadores específicos**:
  - `Glock`: Multiplicador x1.2.
  - `AWP`: Multiplicador x1.5.
  - `Ak47`: Multiplicador x2.0.
  - `ArmaBlanca`: Multiplicador x3.0 con factor inverso para StatTrak (exclusiva rareza dorada).

### 2. Rarezas y Valores Base
Las rarezas se administran mediante estructuras nativas:
- `RAREZAS`: `["azul", "violeta", "rosada", "roja", "dorada"]`
- `VALORES_RAREZA`:
  - `"azul"`: $100
  - `"violeta"`: $150
  - `"rosada"`: $300
  - `"roja"`: $600
  - `"dorada"`: $1000

### 3. Jerarquía de Cajas (`clases_caja.py`)
- **`Caja` (ABC)**:
  - Atributos: `id`, `nombre`, `lootpool`, `precio`.
  - Método: `abrir(id_nueva_arma) -> Arma` (consume funciones de semilla de `Funciones.py`).
- **Cajas concretas**:
  - `Kilovatio` ($250)
  - `DreamsAndNightmares` ($300)
  - `Revolucion` ($350)

### 4. Usuario y Mercado (`clase_usuarios.py`, `clases_oferta_mercado.py`)
- **`Usuario`**:
  - Control de fondos (`conseguir_fondos`, `gastar_fondos`).
  - Inventario de armas y cajas (`agregar_arma`, `quitar_arma`, `agregar_caja`, `abrir_caja`, `valor_inventario`).
- **`Oferta`**:
  - Representa una publicación en el mercado con estados: `"En venta"`, `"Vendida"`, `"Cancelada"`.
- **`Mercado`**:
  - `publicar_oferta(vendedor, arma, precio)`
  - `cancelar_oferta(oferta)`
  - `comprar_oferta(oferta, comprador)`

---

## 🎲 Control de Semilla y Orquestación (`Funciones.py`)

### Gestión de Semilla
- Almacena una variable global `semilla` (por defecto `42`).
- Las funciones pseudoaleatorias (`choices`, `uniform`, `randint`, `random_float`) fijan `random.seed(semilla)`, generan el valor determinista y **alteran y guardan automáticamente la semilla** para la siguiente llamada.
- `obtener_semilla()` y `modificar_semilla(nueva_semilla)` permiten auditoría y reproducibilidad exacta.

### Funciones Orquestadoras del Mercado
- `gestionar_compra_y_apertura_caja(usuario, caja)`: Valida saldo, asigna caja, genera ID autoincremental, abre caja, calcula cotización, evalúa ROI y audita en el log.
- `gestionar_publicacion_oferta(mercado, vendedor, arma, ...)`: Valida tenencia, calcula precio sugerido (+margen) y publica en el mercado.
- `gestionar_compra_oferta(mercado, comprador, oferta, ...)`: Previene auto-compras, transfiere fondos y armas, retiene comisión del mercado (5%) y audita saldos.
- `gestionar_cancelacion_oferta(mercado, solicitante, oferta)`: Cancela y devuelve el arma al inventario.
- `gestionar_busqueda_y_filtrado(mercado, ...)`: Filtra por tipo, rareza, StatTrak o precio máximo.
- `gestionar_liquidacion_masiva(mercado, usuario, ...)`: Publica en lote armas de bajo valor con descuento rápido.
- `gestionar_informe_completo_mercado(mercado, usuarios)`: Resumen financiero global y patrimonial.

---

## 🚀 Ejecución

### 1. Ejecución Principal
Para ejecutar la simulación del mercado:
```bash
python main.py
```

### 2. Pruebas Unitarias
Para correr la suite de pruebas unitarias automatizadas:
```bash
python -m unittest test_mercado.py
```
*(11 pruebas cubriendo determinismo de semilla, validaciones de rarezas, fórmulas de armas, aperturas de cajas, transferencias bancarias y comisiones).*

