# POS Abarrotes — Tienda Periquita

Punto de venta de escritorio para una tienda de abarrotes real: ventas con
lector de código de barras, inventario, cortes de caja por vendedor,
compras a proveedores, apartados, préstamos y reportes. Lo usa el personal
de la tienda (no técnicos) en una sola computadora con Windows.

## Stack

- **Lenguaje:** Python 3.13 (en Windows se invoca con `py`, no `python`)
- **UI:** PySide6 (Qt) — aplicación de escritorio, tema oscuro Catppuccin Mocha
- **Base de datos:** SQLite (modo WAL) — archivo `abarrotes_pos.db` creado
  junto al programa, con respaldo automático `abarrotes_pos_respaldo.db`
- **Tests:** pytest (`tests/`)
- **Empaquetado:** PyInstaller → `.exe` de un archivo (no se commitea)
- **Arquitectura:** TODO el código vive en `pos_abarrotes.py` (~7,000
  líneas, un solo archivo a propósito: facilita empaquetar y copiar)

## Comandos

- `py pos_abarrotes.py` — arranca la app en local (crea la BD si no existe)
- `py -m pytest` — corre los tests (deben pasar antes de cada commit)
- `py -m PyInstaller --onefile --noconsole pos_abarrotes.py` — genera el .exe
- No hay lint ni build de otro tipo configurados.

## Estructura del proyecto

- `pos_abarrotes.py` — TODA la aplicación (fuente canónica, v3)
- `assets/` — mascota "perrito": frames pixel-art y `perrito_config.json`
  (frases/animaciones configurables sin tocar código)
- `tests/` — tests de la lógica sin UI; usan BD temporal, NUNCA la real
- `spec/` — constitución del proyecto y specs de features (SDD)
- `docs/` — guías de trabajo, checklist de seguridad y bitácoras de sesión
- `.claude/` — skills, comandos y agentes del arnés
- `ando-haciendo-un-proyecto-de-un/` — carpeta histórica de trabajo, NO es
  fuente. No editar nada ahí; la fuente canónica es `pos_abarrotes.py` raíz.
- `build/`, `dist/`, `*.exe`, `*.db` — artefactos locales, ignorados por git

## Convenciones

- Código, comentarios, UI y documentación **en español**.
- Nombres de funciones/variables en `snake_case` español
  (`obtener_o_crear_cliente`, `resumen_caja_sesion`).
- Fechas SIEMPRE como texto `"%Y-%m-%d %H:%M:%S"` vía
  `datetime.now().strftime(...)`.
- Dinero en `REAL` (float); cantidades/stock hoy son `INTEGER`.
- Borrado lógico con columna `activo` (0/1), nunca `DELETE` físico de
  productos/clientes/usuarios.
- Migraciones de esquema SOLO aditivas con `agregar_columna_si_falta()`
  dentro de `crear_tablas()` — nunca `ALTER` destructivo ni `DROP`.
- Diálogos de UI siguen el patrón `Dialogo<Cosa>(QDialog)` con
  `QFormLayout` + `QDialogButtonBox`; casillas numéricas usan
  `CasillaEntero`/`CasillaMonto` (seleccionan todo al enfocar).
- Errores de BD se traducen a mensaje humano con `mensaje_error_db(e)`.
- Ver skills en `.claude/skills/` para el esquema exacto de BD y las
  reglas de negocio de caja.

### Invariantes del dominio (ningún cambio debe romperlos)

- Toda venta descuenta stock y registra `detalle_ventas` con costo del
  momento (la ganancia histórica no cambia si luego cambia el costo).
- Todo movimiento de stock deja rastro en `movimientos_inventario`.
- Todo cambio de precio deja rastro en `historial_precios`.
- Las ventas/cortes/KPIs se atribuyen al `vendedor_nombre` del turno.
- La BD existente de la tienda SIEMPRE debe poder abrirse con la versión
  nueva del código (compatibilidad hacia atrás del esquema).

## No hagas

- NO toques, borres ni commitees `abarrotes_pos.db` ni
  `abarrotes_pos_respaldo.db`: son datos REALES de la tienda.
- NO corras tests ni scripts contra la BD real; usa BD temporal.
- Sin dependencias nuevas sin avisar (hoy solo PySide6 + pytest).
- No dividir `pos_abarrotes.py` en módulos sin decisión explícita del
  usuario (está en un archivo a propósito).
- No debilitar ni borrar tests para que pasen.
- No commitees secretos, `.exe`, `.db` ni artefactos de build (el repo en
  GitHub es accesible: trátalo como público).
- No cambies contraseñas/usuarios iniciales sin plan de migración (hay
  instalaciones reales activas).

## Flujo de trabajo

- **Spec-anchored (SDD):** toda feature pasa por `spec/features/NNN-*`
  (usar `/nueva-feature`). La spec se mantiene viva: si la implementación
  se desvía, se actualiza la spec ANTES de seguir.
- **Flujo estricto:** presenta plan y espera OK del usuario antes de
  cualquier tarea no trivial (esquema de BD, flujos de dinero, UI nueva).
- Si no estás seguro al 80%, pregunta. No inventes.
- Al retomar sesión: leer la bitácora más reciente en `docs/sesiones/` +
  `spec/constitution/roadmap.md`. Al cerrar: `/cierre-sesion`.
- Mentalidad: el humano dirige, la IA ejecuta; el humano es el responsable
  final y Validador de Intentos.

## Documentación

- `docs/README.md` — mapa de toda la infraestructura y el flujo en una frase
- `spec/constitution/` — misión, stack normativo y roadmap
- `docs/guia-prompts.md` — cómo pedir trabajo (con ejemplos de este repo)
- `docs/guia-ejecucion.md` — Plan Mode vs Build vs `/nueva-feature`, subagentes, loops
- `docs/checklist-seguridad.md` — principios y amenazas de ESTE proyecto
- `docs/sesiones/` — bitácoras (memoria entre sesiones)
- Skills: `.claude/skills/` (esquema-bd, reglas-caja, convenciones-ui)
- Comandos: `/test`, `/arregla-tests`, `/nueva-feature`, `/deploy-check`, `/cierre-sesion`
