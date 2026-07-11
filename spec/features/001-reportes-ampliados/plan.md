# Plan — 001: Reportes ampliados

> Requiere spec.md APROBADA y sin preguntas abiertas. ✅ (2026-07-08)

## Enfoque

La lógica nueva se escribe como **funciones a nivel de módulo, sin UI**
(igual que `resumen_caja_sesion`), para poder testearlas con la fixture
`bd_temporal` existente: `periodo_anterior()` (cálculo puro de fechas),
`metricas_periodo()` (venta, ganancia, nº ventas, ticket promedio de un
rango), `ventas_por_dia()` / `ventas_por_hora_rango()` /
`ganancia_por_categoria_rango()` (datos para gráficas, reutilizando la
misma expresión de costo `COALESCE(NULLIF(d.costo_total,0), d.cantidad *
p.precio_compra, 0)` que ya usan los reportes para que las cifras
cuadren), y `exportar_tabla_csv()` (módulo `csv` de stdlib, UTF-8 con BOM
para que Excel lo abra con acentos).

La UI añade dos sub-pestañas al `QTabWidget` de Reportes Admin
(«Comparativa» y «Gráficas») y dos botones («Exportar CSV», «Exportar
PDF») en la barra del rango de fechas. La exportación lee la
`QTableWidget` **visible** (encabezados + celdas), de modo que un solo
par de funciones sirve para las 10 tablas actuales y la comparativa sin
duplicar consultas; en la pestaña «Gráficas» los botones se deshabilitan.
El PDF se genera con `QTextDocument.print_()` sobre HTML (Qt, sin
dependencia nueva). Las gráficas usan **QtCharts** (ya incluido en
PySide6). `_cargar_reportes_fuertes()` pasa a refrescar también
comparativa y gráficas.

Semanas = lunes a domingo. «Rango libre vs anterior» = mismo número de
días inmediatamente antes del inicio del rango.

**Alternativa descartada:** matplotlib para gráficas y openpyxl para
Excel — ambas son dependencias nuevas que engordan el `.exe` de
PyInstaller y el CSV/QtCharts cubren la necesidad. También se descartó
re-ejecutar el SQL de cada reporte al exportar: exportar la tabla en
pantalla garantiza que el archivo es exactamente lo que el usuario ve.

## Archivos / secciones afectadas

| Archivo · sección | Cambio |
|-------------------|--------|
| `pos_abarrotes.py` · imports | añadir `csv`, `QtCharts`, `QTextDocument`/`QPdfWriter` (todo stdlib/PySide6) |
| `pos_abarrotes.py` · funciones de lógica (junto a `resumen_caja_sesion`) | nuevas: `periodo_anterior`, `metricas_periodo`, `ventas_por_dia`, `ventas_por_hora_rango`, `ganancia_por_categoria_rango`, `exportar_tabla_csv`, `tabla_a_html` (para PDF) |
| `pos_abarrotes.py` · `_crear_tab_reportes_fuertes` | botones Exportar CSV/PDF; sub-pestañas «Comparativa» (tabla de métricas + botones de periodo rápido) y «Gráficas» (4 `QChartView`) |
| `pos_abarrotes.py` · `_cargar_reportes_fuertes` | además de las tablas, refresca comparativa y gráficas con el rango vigente |
| `pos_abarrotes.py` · métodos nuevos de UI | `_exportar_reporte_csv`, `_exportar_reporte_pdf`, `_cargar_comparativa`, `_cargar_graficas` |
| `tests/test_reportes.py` (nuevo) | tests de `periodo_anterior`, `metricas_periodo` (con ventas sembradas en `bd_temporal`), series de gráficas y `exportar_tabla_csv`; caso «periodo sin ventas» |

## Datos / estado nuevos

**Ninguno.** La feature es solo lectura: cero tablas, cero columnas,
cero escrituras en la BD.

## Impacto por capa

- **BD:** ninguno (solo `SELECT`; sin migraciones).
- **Lógica de negocio:** funciones nuevas de agregación por periodo;
  reutilizan la expresión de costo existente — no cambian ningún cálculo
  actual.
- **UI:** 2 sub-pestañas y 2 botones nuevos dentro de Reportes Admin
  (solo visible para admin, como hoy); resto de pestañas intactas.
- **Reportes / corte de caja:** los reportes actuales no cambian; el
  corte de caja no se toca.

## Riesgos

- **QtCharts no incluido en el `.exe`** → PyInstaller tiene hook para
  PySide6-Addons, pero se verifica generando el exe en `/deploy-check`
  antes de entregar; si fallara, se añade `--collect-all PySide6` al
  comando documentado.
- **Cifras de comparativa no cuadran con las tablas** → usar exactamente
  la misma expresión de costo/ganancia y los mismos límites
  `00:00:00`–`23:59:59`; criterio de aceptación explícito lo verifica.
- **CSV con acentos roto en Excel** → escribir con `utf-8-sig` (BOM) y
  probarlo en el test.
- **Ticket promedio con división entre cero** (periodo sin ventas) →
  las funciones devuelven 0 explícito; test dedicado.
- **Rendimiento con rangos largos** → mismas tablas y filtros por fecha
  que los reportes actuales ya usan sin problema; sin riesgo nuevo real.
