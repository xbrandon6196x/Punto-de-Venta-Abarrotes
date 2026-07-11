# Spec — 001: Reportes ampliados

> Estado: APROBADA · Fecha: 2026-07-08

## Qué

El administrador podrá ver, en la pestaña de Reportes Admin, cómo va la
tienda comparada contra el periodo anterior (esta semana vs la pasada,
este mes vs el pasado, o cualquier rango contra su equivalente anterior),
con la diferencia en pesos y en porcentaje. Además verá gráficas de sus
ventas (por día, por hora, por categoría y la tendencia contra el periodo
anterior) y podrá exportar cualquier reporte a un archivo CSV (que abre
en Excel) o PDF para imprimir o archivar.

## Por qué

Hoy los reportes muestran solo el rango elegido: no hay forma de saber si
la tienda vendió más o menos que la semana o el mes pasado sin anotar
números a mano. Tampoco se puede sacar nada de la computadora — no hay
exportación ni impresión — y los números en tabla no dejan ver de un
vistazo los días y horas pico. El dueño necesita esto para decidir
compras, horarios y ofertas.

## Alcance

**Incluye:**
- Nueva sub-pestaña **«Comparativa»** en Reportes Admin con:
  - Botones de periodo rápido: «Esta semana vs pasada», «Este mes vs
    pasado», y el rango libre actual comparado contra el periodo
    equivalente inmediato anterior (misma duración).
  - Métricas comparadas: venta total, ganancia, número de ventas y
    ticket promedio — cada una con valor actual, valor anterior,
    diferencia en $ y en %.
- Nueva sub-pestaña **«Gráficas»** en Reportes Admin con (QtCharts, ya
  incluido en PySide6):
  - Ventas por día (barras) del rango elegido.
  - Ventas por hora (barras).
  - Ganancia por categoría (barras).
  - Tendencia de venta diaria (línea) del periodo actual encimada con la
    del periodo anterior.
- Botones **«Exportar CSV»** y **«Exportar PDF»** en Reportes Admin que
  exportan el sub-reporte visible (las 10 tablas actuales y la
  comparativa). El destino lo elige el usuario con el diálogo estándar
  de guardar archivo. El PDF lleva título del reporte, rango de fechas
  y fecha de generación.
- Tests de la lógica nueva (cálculo de comparativas y generación de CSV)
  con BD temporal.

**NO incluye (explícito):**
- Excel real (`.xlsx`): el CSV abre en Excel; si algún día hace falta
  formato nativo se hará como feature aparte (requiere openpyxl).
- Exportación en la pestaña «Ventas del Día» de los vendedores (los
  reportes exportables son solo los de admin).
- Envío por correo, impresión directa a impresora de tickets, o
  reportes programados/automáticos.
- Cambios de esquema de BD: esta feature es **solo lectura** de datos.
- Exportar las gráficas como imagen (solo se ven en pantalla).

## Criterios de aceptación

Verificables uno a uno. El verificador los revisará contra el diff real.

- [ ] En Reportes Admin aparece la sub-pestaña «Comparativa»; al elegir
      «Esta semana vs pasada» se ven venta, ganancia, nº de ventas y
      ticket promedio de ambas semanas con diferencia en $ y %.
- [ ] «Este mes vs pasado» hace lo mismo con meses calendario.
- [ ] Con un rango libre (p. ej. 10 días), la comparativa usa los 10 días
      inmediatos anteriores como periodo de comparación.
- [ ] La sub-pestaña «Gráficas» muestra las 4 gráficas (día, hora,
      categoría, tendencia vs periodo anterior) con los datos del rango
      elegido, y se actualizan al cambiar el rango.
- [ ] Con el reporte «Top vendidos» visible, «Exportar CSV» genera un
      archivo con las mismas columnas y filas que la tabla en pantalla;
      lo mismo aplica a cualquiera de las 10 tablas y a la comparativa.
- [ ] «Exportar PDF» genera un PDF legible con título, rango de fechas,
      fecha de generación y la tabla del reporte visible.
- [ ] Un periodo sin ventas no truena: comparativa muestra ceros y las
      gráficas quedan vacías sin error.
- [ ] Las cifras de la comparativa cuadran con lo que ya reportan las
      tablas existentes para el mismo rango (misma fuente de datos).
- [ ] `py -m pytest` en verde (incluyendo tests nuevos de esta feature).
- [ ] La app arranca (`py pos_abarrotes.py`) y el flujo tocado funciona.
- [ ] Una BD existente de la tienda (esquema anterior) abre sin error.
- [ ] El corte de caja sigue cuadrando (la feature no toca dinero: solo
      lee; verificar que no se escribió nada).

## Preguntas abiertas

Resolver TODAS antes de pasar a plan.md.

- [x] ¿Formatos de exportación? → CSV + PDF, sin dependencias nuevas
      (2026-07-08, dueño).
- [x] ¿Qué comparativas? → semana vs anterior, mes vs anterior y rango
      libre vs periodo equivalente anterior (2026-07-08, dueño).
- [x] ¿Qué gráficas? → las 4: día, hora, categoría y tendencia con
      periodo anterior (2026-07-08, dueño).
- [x] ¿Qué reportes se exportan? → todos los de Reportes Admin
      (2026-07-08, dueño).
