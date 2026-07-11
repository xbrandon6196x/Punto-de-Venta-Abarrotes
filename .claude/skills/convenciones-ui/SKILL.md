---
name: convenciones-ui
description: Usar siempre que se cree o modifique UI (PySide6/Qt): diálogos, pestañas, tablas, estilos, colores o widgets en pos_abarrotes.py.
---

# Convenciones de UI (PySide6)

La app es una `QMainWindow` con `QTabWidget` (pestañas por módulo: venta,
inventario, reportes…). El usuario final es personal de tienda sin perfil
técnico: textos en español claro, botones grandes, atajos de teclado.

## Tema y colores (Catppuccin Mocha — usar EXACTAMENTE estos)

Todo el estilo vive en la constante global `ESTILO` (QSS). No agregues
stylesheets sueltos por widget si se puede resolver en `ESTILO` con
`objectName` (patrón existente: `QLabel#lbl_titulo`, `QLabel#lbl_total`).

| Uso | Hex |
|-----|-----|
| Fondo principal | `#1e1e2e` |
| Fondo tablas / campos | `#181825` |
| Superficie (tabs, statusbar) | `#313244` |
| Bordes / gridlines | `#45475a` |
| Texto normal | `#cdd6f4` |
| Texto secundario | `#a6adc8` |
| Acento / selección / títulos | `#89b4fa` |
| Éxito / totales de dinero | `#a6e3a1` |

## Patrones obligatorios

- **Diálogo nuevo** = clase `Dialogo<Cosa>(QDialog)` con `QFormLayout` (o
  `QGridLayout`) + `QDialogButtonBox` para OK/Cancelar. Mira
  `DialogoAjusteStock` o `DialogoAbonoApartado` como referencia antes de
  escribir uno.
- **Casillas numéricas**: NUNCA `QSpinBox`/`QDoubleSpinBox` directos; usar
  `CasillaEntero` y `CasillaMonto` (mixin que selecciona todo el valor al
  enfocar — crítico para captura rápida en caja).
- **Tablas**: `QTableWidget` con `setAlternatingRowColors(True)` y
  `QHeaderView.Stretch`/`ResizeToContents` según columna; montos alineados a
  la derecha y formateados `f"${monto:,.2f}"`.
- **Errores al usuario**: `QMessageBox` con texto en español; errores de BD
  pasan por `mensaje_error_db(e)` para traducirlos a lenguaje humano.
- **Fechas en pantalla**: separar con `separar_fecha_hora()`; meses en
  español con `MESES_ES`.
- Código de barras `MANUAL-...` jamás se muestra crudo: usar `codigo_visible()`.

## Estructura del archivo

Todo vive en `pos_abarrotes.py` (~7,000 líneas) en este orden: configuración
→ estilo → funciones de BD → validadores → mixins/casillas → diálogos →
mascota (`AsistentePerrito`) → pestañas/ventana principal → `main`. Coloca
código nuevo en la sección que le corresponde, no al final del archivo.

## Verificación tras tocar UI

- `py pos_abarrotes.py` debe arrancar sin traceback y la pestaña tocada
  debe abrirse (los tests no cubren UI).
- Revisar en tema oscuro que el texto nuevo sea legible (no hardcodear
  negro/blanco: usa los hex de la tabla).
- Si tocaste el flujo de cobro, probar con lector simulado: teclear un
  código y Enter.
