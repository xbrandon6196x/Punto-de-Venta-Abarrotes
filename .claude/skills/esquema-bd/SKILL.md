---
name: esquema-bd
description: Usar siempre que se toque SQL, sqlite3, crear_tablas, migraciones, o cualquier tabla de abarrotes_pos.db (productos, ventas, apartados, prestamos, sesiones_usuario…) en pos_abarrotes.py.
---

# Esquema de la base de datos (abarrotes_pos.db)

SQLite en modo WAL. La BD se crea junto al programa (`DB_NAME = "abarrotes_pos.db"`,
ruta relativa al directorio de trabajo). Respaldo automático en
`abarrotes_pos_respaldo.db` vía `asegurar_base_guardada()`. Conexión SIEMPRE con
`conectar()` (activa `foreign_keys`, `busy_timeout=5000`, WAL, `synchronous=FULL`).

## Las 17 tablas (definidas en `crear_tablas()`)

| Tabla | Rol | Columnas clave |
|-------|-----|----------------|
| `usuarios` | cuentas login | `usuario` UNIQUE, `rol`, `password_hash` (SHA-256), `activo` |
| `sesiones_usuario` | turnos de caja | `inicio`/`fin`, `fondo_inicial`, `efectivo_contado`, `diferencia_efectivo`, `corte_cerrado`, `estado` ('ABIERTA') |
| `productos` | inventario | `codigo_barras` UNIQUE NOT NULL, `precio_compra`, `precio_venta`, `stock` INTEGER, `stock_minimo` (def. 5), `activo` |
| `ventas` | cabecera venta | `total`, `metodo_pago`, `efectivo_recibido`, `usuario_id`, `sesion_id`, `vendedor_nombre` |
| `detalle_ventas` | renglones | `cantidad` INTEGER, `precio_unitario`, `costo_unitario`, `subtotal`, `costo_total` |
| `movimientos_inventario` | auditoría stock | `tipo_movimiento`, `cantidad`, `motivo` |
| `historial_precios` | auditoría precios | precios anterior/nuevo de compra y venta, `motivo` |
| `proveedores` | catálogo | `nombre` UNIQUE, `activo` |
| `compras` / `detalle_compras` | entradas de mercancía | actualizan stock y costos |
| `ticket_pendiente` / `detalle_ticket_pendiente` | autoguardado del ticket en curso | PK = `usuario_id` (uno por usuario) |
| `clientes` | para apartados/préstamos | `nombre`, `telefono`, `correo`, `activo` |
| `apartados` / `abonos_apartado` | apartados con anticipos | `estado` 'ACTIVO'→cierre; abono `tipo` 'ABONO'/'DEVOLUCION' |
| `prestamos` / `detalle_prestamos` | fiado de productos | detalle `estado`: 'PRESTADO'→'DEVUELTO'/'COBRADO' (+`venta_id`) |
| `movimientos_cliente` | historial por cliente | `tipo_movimiento`, `referencia`, `monto` |

## Reglas duras

1. **Migraciones SOLO aditivas**: columna nueva = `agregar_columna_si_falta(conn,
   tabla, columna, definicion)` al final de `crear_tablas()`. PROHIBIDO `DROP`,
   renombrar columnas o cambiar tipos: hay BDs reales en producción en la tienda
   que deben abrir con el código nuevo sin paso manual.
2. **Fechas**: TEXT `"%Y-%m-%d %H:%M:%S"` (orden lexicográfico = cronológico; los
   reportes filtran con `>=`/`<=` de strings). No usar otro formato ni tipos DATE.
3. **Borrado lógico**: `activo = 0`. Nunca DELETE de productos/clientes/usuarios
   (romperían los FK de historial).
4. **Valores de enum en texto** (respetar mayúsculas exactas):
   - `metodo_pago`: `'Efectivo' | 'Tarjeta' | 'Transferencia' | 'Otro'`
   - `apartados.estado`: `'ACTIVO'` y estados de cierre; `abonos_apartado.tipo`: `'ABONO' | 'DEVOLUCION'`
   - `detalle_prestamos.estado`: `'PRESTADO' | 'DEVUELTO' | 'COBRADO'`
   - `sesiones_usuario.estado`: `'ABIERTA'` (cierre vía `corte_cerrado=1`)
5. **Códigos manuales**: productos sin código de barras usan
   `MANUAL-<timestamp>` (`generar_codigo_manual()`); en UI se muestran como
   "Sin código" (`codigo_visible()`). `codigo_barras` nunca puede ser NULL/''.
6. **Cantidades y granel (feature 003):** `productos.es_granel` (0/1)
   marca el modo. Para productos a granel, `stock` y las columnas
   `cantidad` guardan kg con decimales (la afinidad de SQLite almacena
   REAL en la columna INTEGER declarada — sin ALTER). Las piezas siguen
   siendo enteras. Comparaciones de peso con `TOLERANCIA_PESO` (1e-6) y
   redondeo al gramo con `redondear_peso()`; formateo SIEMPRE vía
   `formatear_cantidad()` / `formatear_cantidad_mixta()`.

## Después de editar esquema o queries

- Corre `py -m pytest` (los tests crean una BD temporal desde `crear_tablas()`).
- Verifica que una BD "vieja" (sin tus columnas nuevas) abre: los tests de
  migración simulan esto con `agregar_columna_si_falta`.
- NUNCA corras nada contra `abarrotes_pos.db` real de la raíz.
