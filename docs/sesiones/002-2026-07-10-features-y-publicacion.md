# Sesión 002 — 2026-07-08 al 10 — Features 1-4 y publicación limpia

## Qué se hizo

- **Feature 001 — Reportes ampliados** (`spec/features/001-reportes-ampliados`):
  sub-pestañas «Comparativa» (semana/mes/rango vs periodo anterior) y
  «Gráficas» (QtCharts: día, hora, categoría, tendencia) en Reportes
  Admin; exportar CSV (utf-8-sig) y PDF (QPdfWriter A4 horizontal) de la
  tabla visible. Lógica sin UI en `pos_abarrotes.py` (`periodo_anterior`,
  `metricas_periodo`, `ventas_por_dia`…) + `tests/test_reportes.py`.
  Verificador: APROBADO 12/12. Bug real corregido: el bucle de cortes
  reasignaba `inicio`/`fin` dentro de `_cargar_reportes_fuertes`.
- **Feature 002 — Contraseñas PBKDF2** (`spec/features/002-endurecer-contrasenas`):
  hash con sal en la misma columna (`pbkdf2$iter$sal$hash`), migración
  silenciosa de hashes SHA-256 al primer login, `DialogoCambioContrasena`
  (voluntario + reseteo admin), botón «🔑 Contraseña» en statusbar, login
  sin pista de credenciales. `tests/test_contrasenas.py`. Verificador:
  APROBADO. Login real con 600k iteraciones: 0.41 s.
- **Feature 003 — Productos a granel** (`spec/features/003-productos-a-granel`):
  columna aditiva `es_granel` (ÚNICO cambio de esquema — la afinidad de
  SQLite guarda decimales en las columnas INTEGER sin ALTER),
  `DialogoVentaGranel` (kg⇄gr sincronizados, monto exacto, atajos ¼-1 kg),
  `CasillaPeso`, stock/compras/préstamos por peso, formateo unificado
  (`formatear_cantidad`/`_mixta`), skill esquema-bd actualizada.
  `tests/test_granel.py` + `tests/test_granel_flujos.py` (ventana real
  offscreen). Verificador: ciclo 1 CON RESERVAS → 4 correcciones →
  ciclo 2 APROBADO.
- **Feature 004 — Primer arranque sin claves** (`spec/features/004-primer-arranque`):
  `USUARIOS_INICIALES` eliminado; `DialogoPrimerUsuario` crea admin y
  vendedor con claves del dueño en BD nueva; `crear_usuario()` /
  `hay_usuarios_activos()`; conftest siembra usuarios de prueba; test
  guardián de claves (invertidas). El «cambio sugerido» de la 002 quedó
  sustituido (ya no hay lista de claves por defecto).
- **Perrito:** frases ~37→~90 + eventos nuevos (granel, compra, exportar,
  password) con animación propia en modo aleatorio; travesuras cada ~21 s;
  se detiene mientras habla. `assets/perrito_config.json` sincronizado.
- **Publicación a GitHub:** historial local reescrito con `git commit-tree`
  (5 commits limpios, sin el commit raíz que traía las BDs reales y el
  `.exe`); `/deploy-check` BLOQUEÓ claves históricas en docs/specs/tests →
  saneadas (`c954c29`); force-push a `origin/main`. Rama local
  `respaldo-pre-limpieza` conserva la historia previa (NO subir).
- **Entregable:** `dist/POS-Tienda-Periquita/` (exe 47 MB + assets +
  LEEME.txt) y `dist/POS-Tienda-Periquita.zip` (59.8 MB). Exe probado:
  arranca, QtCharts empaquetado OK, BD copia de la tienda abre y migra.

## Decisiones

- Cambio de clave por defecto: obligatorio → sugerido → eliminado junto
  con las claves (ver `spec/features/002-*/spec.md` y `004-*/spec.md`).
- Las claves históricas no se nombran en NINGÚN archivo trackeado; el
  test guardián las guarda invertidas (`tests/test_contrasenas.py`).
- Historial de GitHub reemplazado por force-push; el purge definitivo de
  commits huérfanos depende de volver privado el repo (pendiente dueño).
- Riesgo de granel re-evaluado: sin migración de tipos gracias a la
  afinidad de SQLite (ver `spec/features/003-*/plan.md`).

## Pendiente / siguiente paso

1. **DUEÑO: volver PRIVADO el repo** `xbrandon6196x/Punto-de-Venta-Abarrotes`
   (Settings → Danger Zone → Change visibility). Hasta entonces los
   commits viejos con BDs/claves pueden seguir accesibles por SHA.
2. Llevar `dist/POS-Tienda-Periquita/` a la tienda (instrucciones en su
   LEEME.txt) y probar en sitio: login con claves de siempre + venta a
   granel real.
3. Siguiente feature del roadmap: multi-equipo/red (alto riesgo, requiere
   actualizar la constitución) — solo con OK explícito del dueño.

## Estado del repo

- **Rama:** main = `c954c29`, empujada a origin/main (force). Ramas
  locales extra: `respaldo-pre-limpieza` (historia previa, no subir).
- **Sin commitear:** nada (`git status` limpio; `dist/` y BDs ignorados).
- **Tests:** 40 pasan (~10-40 s según caché; 3 son de ventana Qt offscreen).
