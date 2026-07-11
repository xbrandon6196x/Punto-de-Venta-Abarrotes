# Plan — 003: Productos a granel (kg/gr)

> Requiere spec.md APROBADA y sin preguntas abiertas. ✅ (2026-07-09)

## Enfoque

**Hallazgo clave que baja el riesgo del roadmap:** SQLite guarda
decimales en columnas declaradas `INTEGER` sin ninguna migración (la
afinidad de tipos almacena `9.75` como REAL en la misma columna;
verificado en esta máquina). Por lo tanto NO hay `ALTER` de tipos ni
migración destructiva: `stock` y las columnas `cantidad` existentes
aceptan pesos decimales tal cual. El único cambio de esquema es la
columna aditiva `es_granel INTEGER DEFAULT 0` en `productos`, vía
`agregar_columna_si_falta()` — una BD vieja abre y todo sigue por pieza.

Lógica nueva a nivel de módulo (testeable): `redondear_peso(kg)` (3
decimales = gramos), `peso_desde_monto(monto, precio_kg)` (con guardia
de precio 0) y `formatear_cantidad(cantidad, es_granel)` («3» para
piezas, «0.250 kg» para granel) — TODO formateo de cantidades pasa por
ahí para no regar `str(int(...))` por el archivo.

UI: `CasillaPeso` (QDoubleSpinBox de 3 decimales con el mixin de
selección, sufijo « kg»), casilla nueva junto a `CasillaEntero`/
`CasillaMonto`. `DialogoVentaGranel(QDialog)` con: kg y gramos
sincronizados (señales con guardia anti-bucle), monto en $ que calcula
el peso (se cobra el monto EXACTO tecleado y se registra el peso al
gramo), atajos ¼/½/¾/1 kg y vista previa «0.250 kg × $180.00/kg =
$45.00». Al agregar al ticket un producto con `es_granel=1` se abre este
diálogo en lugar de sumar 1 pieza; el renglón del ticket muestra el peso.
En inventario, `DialogoProducto` gana el checkbox «Se vende a granel
(precio por kilo)» y su campo de stock cambia a `CasillaPeso` cuando
está marcado; mismo trato para ajuste de stock, compras y préstamos
(cantidad decimal solo si el producto es granel). La validación de stock
insuficiente compara floats con tolerancia de 1 miligramo (1e-6 kg) y
reutiliza los mensajes humanos existentes.

Reportes/corte: sin cambios de fórmula — las sumas SQL ya operan floats;
solo el formateo de columnas «Cantidad» usa `formatear_cantidad` para no
mostrar «3.0» en piezas. La fórmula del corte no toca cantidades.

**Alternativa descartada:** guardar el peso como gramos enteros
(INTEGER puro) — evita floats pero obliga a convertir en TODOS los
cálculos (precio por kg vs gramos), confunde 1 pieza con 1 gramo en las
columnas compartidas y no hace falta dada la afinidad de SQLite. También
se descartó una tabla `productos_granel` aparte (duplica el catálogo y
rompe los JOIN existentes de reportes).

## Archivos / secciones afectadas

| Archivo · sección | Cambio |
|-------------------|--------|
| `pos_abarrotes.py` · `crear_tablas()` | `agregar_columna_si_falta(productos, es_granel, "INTEGER DEFAULT 0")` |
| `pos_abarrotes.py` · lógica sin UI | nuevas `redondear_peso`, `peso_desde_monto`, `formatear_cantidad` |
| `pos_abarrotes.py` · casillas | nueva `CasillaPeso` (3 decimales, mixin de selección) |
| `pos_abarrotes.py` · diálogos | nuevo `DialogoVentaGranel`; `DialogoProducto` (checkbox granel + stock decimal); diálogo de ajuste de stock |
| `pos_abarrotes.py` · pestaña Venta (~3100-3800) | `_agregar_producto_ticket` abre el diálogo granel; renglón y validación de stock con decimales; cobro guarda cantidad decimal |
| `pos_abarrotes.py` · pestaña Inventario (~3850-4350) | alta/edición con granel; tabla muestra stock formateado; ajuste ±peso |
| `pos_abarrotes.py` · pestaña Compras (~6344-6600) | cantidad `CasillaPeso` si el producto es granel |
| `pos_abarrotes.py` · pestaña Préstamos (~5864, 2841) | prestar/devolver/cobrar con peso decimal |
| `pos_abarrotes.py` · reportes | columnas «Cantidad» con `formatear_cantidad` |
| `tests/test_granel.py` (nuevo) | venta por peso y por monto, redondeo, stock decimal, insuficiencia, compra, préstamo+devolución, BD vieja sigue por pieza |
| `.claude/skills/esquema-bd/SKILL.md` | actualizar la nota «stock es INTEGER hoy» al terminar |

## Datos / estado nuevos

- Columna aditiva: `productos.es_granel INTEGER DEFAULT 0` (0 = pieza,
  1 = granel). ÚNICO cambio de esquema.
- Las columnas `stock`/`cantidad` existentes empiezan a contener REAL
  para productos granel (afinidad SQLite; sin ALTER).

## Impacto por capa

- **BD:** una columna aditiva; sin ALTER de tipos, sin DROP. BD vieja
  abre y opera sin paso manual.
- **Lógica de negocio:** cantidades pasan de int implícito a número
  (int o float); los invariantes se conservan: toda venta granel
  descuenta stock, deja `detalle_ventas` con costo por kg del momento y
  rastro en `movimientos_inventario`.
- **UI:** diálogo nuevo de venta granel, checkbox en producto, casillas
  de peso donde aplique; productos por pieza no ven ninguna diferencia.
- **Reportes / corte de caja:** fórmulas intactas; solo formateo de
  cantidades. El corte no usa cantidades (solo $), cuadra igual.

## Riesgos

- **Regar formateos/validaciones enteras sin detectar** → auditoría con
  grep de `CasillaEntero`, `int(`, `stock`, `cantidad` sitio por sitio
  (mapa ya levantado); el verificador revisará con el mismo grep.
- **Comparaciones float de stock** (0.1+0.2 ≠ 0.3) → tolerancia de 1 mg
  en validaciones y `round(_, 3)` al persistir pesos.
- **Vender por monto con precio/kg en 0** → guardia con mensaje humano
  («este producto no tiene precio por kilo»).
- **Confusión kg/gr al teclear** → campos sincronizados visibles ambos +
  vista previa del cobro siempre a la vista (decisión del dueño).
- **Ticket pendiente autoguardado** con cantidades decimales → se prueba
  que sobrevive el ciclo guardar/restaurar sin truncar a int.
- **Riesgo residual del roadmap (era «medio-alto»)** → baja a medio:
  sin migración de tipos, el único punto sistémico es el formateo.
