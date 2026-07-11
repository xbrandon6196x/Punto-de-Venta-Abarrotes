# Spec — 003: Productos a granel (kg/gr)

> Estado: APROBADA · Fecha: 2026-07-09

## Qué

La tienda podrá vender productos por peso — huevo, jamón, queso y lo que
haga falta — además de los productos por pieza de siempre. El vendedor
captura lo que diga el cliente: «dame medio kilo» (teclea el peso, en kg
o en gramos, o toca un atajo de ¼/½/¾/1 kg y el sistema calcula el
precio) o «dame $30 de jamón» (teclea el monto y el sistema calcula el
peso). El inventario de esos productos vive en kilos con decimales, las
compras a proveedor y los ajustes de stock aceptan peso, y también se
puede fiar por peso a los clientes de confianza.

## Por qué

Hoy TODO se vende por pieza entera: no hay forma de cobrar 250 g de
jamón. El personal lo resuelve fuera del sistema (calculadora y un
producto "comodín"), así que el inventario de granel no cuadra nunca, la
ganancia real de esos productos se desconoce y el corte depende de
apuntes manuales. Es la necesidad más mencionada por el dueño para la
operación diaria.

## Alcance

**Incluye:**
- Marcar un producto como **«se vende a granel»** en el inventario: su
  precio de compra/venta pasa a ser POR KILO y su stock se muestra y
  guarda en kg con hasta 3 decimales (gramos).
- **Diálogo de venta a granel** al agregar uno de estos productos al
  ticket, con: campo de peso en kg, campo en gramos (sincronizados),
  campo de monto en $ (calcula el peso), atajos ¼ / ½ / ¾ / 1 kg, y la
  vista previa del cobro. Si el cliente pide un monto, se cobra ESE monto
  exacto y se registra el peso equivalente redondeado al gramo.
- El **ticket y el detalle de venta** muestran el peso vendido (p. ej.
  «0.250 kg») y congelan precio y costo por kg del momento, igual que
  hoy con las piezas.
- **Stock decimal:** la venta descuenta el peso exacto; los movimientos
  de inventario, ajustes de stock y **compras a proveedor** de granel se
  capturan en peso y dejan rastro con decimales.
- **Préstamos (fiado) por peso:** prestar, devolver y cobrar renglones
  de granel con peso; la devolución regresa el peso al stock.
- Los productos por pieza siguen EXACTAMENTE igual (cantidades enteras,
  mismo flujo de siempre); el granel es opcional por producto.
- Reportes, KPIs y corte de caja funcionan con cantidades decimales sin
  cambiar sus fórmulas (la atribución y el efectivo esperado no cambian).
- Tests de: venta por peso y por monto, redondeo, stock decimal,
  préstamo/devolución por peso, compra por peso, y compatibilidad con BD
  existente.

**NO incluye (explícito):**
- **Apartados por peso** (se sigue apartando por pieza; decisión del
  dueño: los anticipos de granel no son caso real).
- Conexión con báscula (el peso se teclea tal como lo marca la báscula
  del mostrador).
- Códigos de barras de balanza (etiquetas con peso embebido).
- Cambiar productos existentes a granel de forma masiva (se marcan uno
  por uno cuando el dueño lo decida).
- Unidades distintas de kg/gr (litros, metros, etc.).

## Criterios de aceptación

Verificables uno a uno. El verificador los revisará contra el diff real.

- [ ] Un producto puede marcarse como granel con precio por kg; en el
      inventario su stock se ve en kg con 3 decimales.
- [ ] Vender 0.250 kg de un granel de $180/kg cobra $45.00, descuenta
      0.250 del stock y deja `detalle_ventas` y `movimientos_inventario`
      con la cantidad 0.250 y el costo por kg del momento.
- [ ] Vender «$30» de ese granel cobra exactamente $30.00 y registra el
      peso equivalente redondeado al gramo (0.167 kg).
- [ ] Los atajos ¼/½/¾/1 kg llenan el peso y actualizan la vista previa;
      los campos kg y gramos se sincronizan entre sí.
- [ ] No se puede vender más peso del stock disponible (mismo mensaje
      humano que hoy con piezas).
- [ ] Una compra a proveedor de granel captura peso decimal, aumenta el
      stock y actualiza costos igual que una compra normal.
- [ ] Un préstamo de granel registra el peso; devolverlo regresa ese peso
      al stock y cobrarlo genera la venta con ese peso.
- [ ] Un producto por pieza se sigue vendiendo con cantidades enteras y
      su flujo no cambia en nada.
- [ ] El corte de caja cuadra con ventas mixtas (piezas + granel) en la
      misma sesión.
- [ ] Los reportes (día, admin, comparativa, gráficas) muestran cifras
      correctas con ventas de granel incluidas.
- [ ] `py -m pytest` en verde (incluyendo tests nuevos de esta feature).
- [ ] La app arranca (`py pos_abarrotes.py`) y el flujo tocado funciona.
- [ ] Una BD existente de la tienda abre sin error; sus productos siguen
      siendo por pieza hasta que alguien los marque como granel.

## Preguntas abiertas

Resolver TODAS antes de pasar a plan.md.

- [x] ¿Captura por peso, por monto o ambos? → ambos, según pida el
      cliente (2026-07-09, dueño).
- [x] ¿Unidad de captura? → ambos campos, kg y gramos sincronizados
      (2026-07-09, dueño).
- [x] ¿Atajos rápidos? → sí: ¼, ½, ¾ y 1 kg (2026-07-09, dueño).
- [x] ¿Dónde aplica? → ventas + inventario/compras + préstamos; apartados
      NO (2026-07-09, dueño).
