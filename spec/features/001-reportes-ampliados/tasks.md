# Tasks — 001: Reportes ampliados

> Cada tarea es pequeña, verificable, y deja la app FUNCIONANDO al
> terminarla (no hay tareas que rompan y "luego se arregla").

## Checklist

- [x] T1. Funciones de lógica sin UI: `periodo_anterior`,
      `metricas_periodo`, `ventas_por_dia`, `ventas_por_hora_rango`,
      `ganancia_por_categoria_rango`, `exportar_tabla_csv`,
      `tabla_a_html`. Verificar: `py -m pytest` sigue en verde y la app
      arranca (aún sin UI nueva).
- [x] T2. Tests de T1 en `tests/test_reportes.py` (ventas sembradas en
      `bd_temporal`, caso sin ventas, CSV con acentos). Verificar:
      `py -m pytest` en verde.
- [x] T3. Botones «Exportar CSV» / «Exportar PDF» en Reportes Admin que
      exportan la tabla visible (deshabilitados en pestañas sin tabla).
      Verificar: app arranca, exportar «Top vendidos» a CSV y PDF y abrir
      los archivos.
- [x] T4. Sub-pestaña «Comparativa»: botones semana/mes/rango libre y
      tabla de métricas con diferencia $ y %. Se refresca desde
      `_cargar_reportes_fuertes`. Verificar: app arranca, cifras cuadran
      con las tablas existentes del mismo rango, y es exportable.
- [x] T5. Sub-pestaña «Gráficas» con las 4 gráficas QtCharts (día, hora,
      categoría, tendencia vs periodo anterior), refrescadas con el
      rango. Verificar: app arranca, gráficas cambian al cambiar rango,
      rango sin ventas no truena.
- [x] T6. Tests de la feature pasan: `py -m pytest` en verde completo (23).
- [x] T7. Criterios de aceptación de spec.md verificados uno a uno
      (subagente verificador sobre `git diff`): **APROBADO**, 12/12.

## Registro

Anotar fechas, desviaciones y decisiones tomadas durante la implementación.
**Si una desviación cambia el «qué» → actualizar spec.md ANTES de seguir.**

| Fecha | Tarea | Nota |
|-------|-------|------|
| 2026-07-08 | — | Spec y plan aprobados por el dueño; arranca implementación. |
| 2026-07-08 | T1–T2 | Lógica y 13 tests nuevos; QtCharts confirmado disponible en PySide6 local. |
| 2026-07-08 | T3 | Exportación lee la tabla visible; PDF A4 horizontal vía QPdfWriter (probado headless). |
| 2026-07-08 | T4–T5 | Bug encontrado por humo: el bucle de cortes en `_cargar_reportes_fuertes` reasigna `inicio`/`fin`; la carga de comparativa/gráficas se movió al inicio del método. Guardia para `applyNiceNumbers` con todo en 0 (avisos NaN de QtCharts). Comparativa y Gráficas quedaron como 1.ª y 2.ª sub-pestaña de Reportes Admin. |
| 2026-07-08 | T6 | `py -m pytest`: 23 en verde; humo headless con capturas OK; app arranca. |
| 2026-07-08 | T7 | Verificador independiente: APROBADO 12/12. Hallazgos menores: (1) PDF podía reportar éxito con archivo bloqueado — CORREGIDO (se verifica existencia/tamaño tras `print_`); (2) exportar sin pulsar Actualizar usa el rango nuevo en el título con filas del rango viejo (borde de UX, pendiente); (3) rango libre igual a mes calendario compara contra mes anterior (deliberado); (4) QtCharts en el .exe se valida en /deploy-check. |
