# Tasks — 003: Productos a granel (kg/gr)

> Cada tarea es pequeña, verificable, y deja la app FUNCIONANDO al
> terminarla (no hay tareas que rompan y "luego se arregla").

## Checklist

- [x] T1. Columna aditiva `es_granel` en `crear_tablas()` + lógica sin
      UI: `redondear_peso`, `peso_desde_monto`, `formatear_cantidad`.
      Verificar: pytest verde, app arranca, BD vieja abre (test de
      migración con BD sin la columna).
- [x] T2. Tests de T1 en `tests/test_granel.py` (redondeo, monto→peso,
      formateo pieza vs granel, columna aparece en BD vieja).
- [x] T3. `CasillaPeso` + checkbox «se vende a granel» en
      `DialogoProducto`/alta de inventario, con stock decimal y tabla de
      inventario formateada. Verificar: crear producto granel desde la
      UI (humo headless) y verlo listado con kg.
- [x] T4. `DialogoVentaGranel` (kg⇄gr, monto→peso, atajos, vista previa)
      + integración en la pestaña Venta: agregar al ticket, validación de
      stock con tolerancia, cobro con cantidad decimal, ticket pendiente
      sobrevive decimales. Verificar: humo headless de venta 0.250 kg y
      venta por monto $30, stock desciende exacto.
- [x] T5. Compras con peso decimal para granel (entrada de mercancía
      actualiza stock/costos). Verificar: humo o test de compra granel.
- [x] T6. Préstamos por peso: prestar/devolver/cobrar granel; la
      devolución regresa el peso al stock. Verificar: test dedicado.
- [x] T7. Reportes y Ventas del Día muestran cantidades formateadas
      (piezas enteras, granel en kg). Verificar: humo de reportes con
      ventas mixtas.
- [x] T8. Actualizar `.claude/skills/esquema-bd/SKILL.md` (nota de stock
      INTEGER → «acepta REAL para granel; es_granel marca el modo»).
- [x] T9. Tests de la feature pasan: `py -m pytest` en verde completo (36).
- [x] T10. Criterios de aceptación de spec.md verificados uno a uno
      (subagente verificador sobre `git diff`): ciclo 1 CON RESERVAS
      (13/13 CUMPLE, 4 hallazgos) → correcciones → ciclo 2 **APROBADO**.

## Registro

Anotar fechas, desviaciones y decisiones tomadas durante la implementación.
**Si una desviación cambia el «qué» → actualizar spec.md ANTES de seguir.**

| Fecha | Tarea | Nota |
|-------|-------|------|
| 2026-07-09 | — | Spec y plan aprobados por el dueño. Hallazgo previo: afinidad SQLite hace innecesaria la migración de tipos; riesgo del roadmap baja. |
| 2026-07-09 | T1–T4 | Columna es_granel + lógica + CasillaPeso + DialogoVentaGranel. Humo: venta 0.250 kg y «$30 exactos» OK, stock 4.583, corte cuadra, ticket pendiente sobrevive decimales. Bug latente corregido: _prestamo_agregar_producto desempaquetaba 6 campos con el SELECT nuevo de 7. |
| 2026-07-09 | T5–T8 | Compras y préstamos por peso (humo: compra 3.5 kg, préstamo 0.750 kg devuelto regresa stock, cobro 1.25 kg genera venta y cierra préstamo). Reportes con formatear_cantidad_mixta. Desviación menor documentada: en ticket/préstamo, «−» quita el renglón granel completo (no hay «una pieza menos» en peso) y «+» reabre la captura. |
| 2026-07-10 | T10 (ciclo 2) | Verificador: APROBADO — los 4 puntos resueltos con evidencia; 39 tests, sin regresiones, BD real intacta. |
| 2026-07-09 | T10 (ciclo 1) | Verificador: CON RESERVAS (13/13 criterios CUMPLE). Correcciones aplicadas: (1) tests de flujo reales en tests/test_granel_flujos.py — venta peso/monto, préstamo+devolución+cobro, compra, préstamo de TODO el stock (drift float); (2) _insertar_lineas_prestamo con TOLERANCIA_PESO y mensaje formateado; (3) mensajes de entrada de inventario con formatear_cantidad; (4) préstamo capturado por monto ahora valúa el renglón como peso×precio (lo que se cobrará), documentado en código. Suite: 39 en verde (~37 s por los 3 tests de ventana Qt offscreen). |
