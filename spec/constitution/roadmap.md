# Roadmap

Ordenado por riesgo/valor: primero lo de menor riesgo. Cada feature se
trabaja con `/nueva-feature` (crea su carpeta en `spec/features/`).

Estados: `PENDIENTE` · `EN SPEC` · `EN DESARROLLO` · `HECHA` · `DESCARTADA`

| # | Feature | Valor | Riesgo | Estado |
|---|---------|-------|--------|--------|
| 1 | **Reportes ampliados**: comparativas por periodo (semana/mes vs anterior), exportar a CSV y PDF, gráficas de ventas (`spec/features/001-reportes-ampliados`) | Alto | Bajo (solo lectura de datos) | HECHA (2026-07-08, verificador APROBADO; falta commit) |
| 2 | **Endurecer contraseñas**: hash con sal (PBKDF2 de stdlib), migrando los hashes existentes al primer login; forzar cambio de las claves por defecto (`spec/features/002-endurecer-contrasenas`) | Medio | Bajo-medio | HECHA (2026-07-09, verificador APROBADO; falta commit) |
| 3 | **Productos a granel (kg/gr)**: vender por peso huevo, jamón, queso, etc. — precio por kg, captura de peso o de monto, stock en decimales (`spec/features/003-productos-a-granel`) | Muy alto (operación diaria real) | Medio (la afinidad de SQLite evita el ALTER de tipos; solo columna aditiva `es_granel` + formateo) | HECHA (2026-07-10, verificador APROBADO en ciclo 2; falta commit) |
| 4 | **Primer arranque sin claves en el código**: DialogoPrimerUsuario crea admin/vendedor con claves del dueño; requisito para publicar el repo (`spec/features/004-primer-arranque`) | Alto (seguridad del repo público) | Bajo | HECHA (2026-07-10) |
| 5 | **Multi-equipo / red**: usar el POS desde más de una computadora o sincronizar la base | Alto | Alto (SQLite es archivo local; requiere decidir arquitectura: carpeta compartida con WAL ≠ seguro, o servidor) | PENDIENTE |

## Notas de descubrimiento (Fase 0 del bootstrap, 2026-07-08)

- No hay TODO/FIXME en el código; `MEJORAS.md` histórico es changelog de lo
  ya hecho (login, cortes, apartados, préstamos, mascota, WAL).
- La #3 es la que el dueño más mencionó (huevo, jamón, queso por kg/gr).
  Va después de la #1 y #2 por riesgo: toca esquema de BD y flujo de dinero;
  conviene tener más tests en verde antes de entrarle.
- La #4 probablemente cambie principios de `tech-stack.md` → requiere
  actualizar la constitución en su spec.
- [PENDIENTE] confirmar prioridades con el dueño antes de arrancar la #1.
