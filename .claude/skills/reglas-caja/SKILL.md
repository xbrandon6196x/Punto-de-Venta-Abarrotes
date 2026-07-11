---
name: reglas-caja
description: Usar siempre que se toque dinero, ventas, cortes de caja, sesiones de vendedor, apartados, préstamos, KPIs o reportes en pos_abarrotes.py.
---

# Reglas de negocio: caja, ventas y dinero

Este POS maneja el dinero REAL de la tienda. Cualquier error aquí es dinero
perdido o un corte que no cuadra. Estas reglas salen del código actual.

## Sesiones y cortes (turnos de caja)

- Al entrar como vendedor se pide el **nombre real del turno** y el **fondo
  inicial**; se abre una fila en `sesiones_usuario` (`iniciar_registro_sesion`).
- Toda venta, abono y préstamo guarda `sesion_id`, `usuario_id` y
  `vendedor_nombre` — los KPIs y cortes se atribuyen por vendedor. Si añades
  una operación de dinero nueva, DEBE guardar esos tres campos.
- **Fórmula del corte** (`resumen_caja_sesion`, no la cambies sin spec):

  ```
  esperado = fondo_inicial
           + ventas en 'Efectivo' de la sesión
           + anticipos/abonos de apartado en 'Efectivo'
           - devoluciones de anticipo
  ```

  Tarjeta/Transferencia/Otro se reportan aparte y NO entran al efectivo
  esperado. Los préstamos cobrados ya están dentro de las ventas (solo se
  desglosan como informativos).
- El cierre guarda `efectivo_contado`, `diferencia_efectivo` y
  `observaciones`, y marca `corte_cerrado = 1` (`cerrar_registro_sesion`).

## Ventas

- Flujo: escanear/buscar producto → ticket → cobrar → `ventas` +
  `detalle_ventas` + descuento de stock + `movimientos_inventario`.
- `detalle_ventas` congela `precio_unitario` y `costo_unitario` DEL MOMENTO:
  la ganancia histórica no se recalcula si luego cambian precios.
- El ticket en curso se autoguarda en `ticket_pendiente` (uno por usuario)
  para sobrevivir cortes de luz; al cobrar o cancelar se limpia.
- Métodos de pago válidos: `Efectivo`, `Tarjeta`, `Transferencia`, `Otro`.

## Apartados (dinero del cliente en la tienda)

- Apartado `ACTIVO` acumula abonos (`abonos_apartado`, tipo `ABONO`); las
  devoluciones de anticipo son tipo `DEVOLUCION` y RESTAN del efectivo del corte.
- Liquidar un apartado genera la venta final (`venta_id` en la fila).
- La deuda del cliente se calcula con `deuda_cliente()` — úsala, no
  reimplementes la suma.

## Préstamos (fiado de productos)

- Prestar descuenta stock de inmediato; cada renglón (`detalle_prestamos`)
  vive en `PRESTADO` hasta que se **devuelve** (regresa stock, `DEVUELTO`) o
  se **cobra** (genera venta normal, `COBRADO` + `venta_id`).

## Clientes

- Reutilizar clientes con `obtener_o_crear_cliente(cursor, ...)` (empata por
  nombre case-insensitive + teléfono); nunca insertar en `clientes` directo.
- Teléfono/correo son opcionales pero si vienen se validan con
  `telefono_valido()` / `correo_valido()`.
- Todo movimiento de dinero de un cliente se registra con
  `registrar_movimiento_cliente()`.

## Usuarios y roles

- Roles: `admin` (reportes, inventario, precios, todo) y vendedor (solo
  caja). Los reportes de ganancia son SOLO de admin — no filtres datos de
  costo/ganancia hacia pantallas de vendedor.
- Passwords con `hash_password()` (SHA-256 sin sal — mejora pendiente en
  roadmap; no guardes nunca texto plano).

## La mascota (perrito)

- Eventos de negocio disparan frases del perrito (`FRASES_PERRITO`: login,
  venta, apartado, abono, prestamo, devolucion…). Si añades una operación
  nueva visible al vendedor, considera su evento; configurable en
  `assets/perrito_config.json` sin tocar código.

## Verificación tras tocar esta zona

- `py -m pytest` en verde.
- Cuadre manual: con BD temporal, simular fondo + venta efectivo + abono +
  devolución y comprobar `esperado` a mano.
- Revisar que nada nuevo escriba montos negativos ni stock negativo sin
  pasar por una validación con mensaje al usuario.
