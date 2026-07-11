# Roadmap

Ordenado por riesgo/valor: primero lo de menor riesgo. Cada feature se
trabaja con `/nueva-feature` (crea su carpeta en `spec/features/`).

Estados: `PENDIENTE` · `EN SPEC` · `EN DESARROLLO` · `HECHA` · `DESCARTADA`

| # | Feature | Valor | Riesgo | Estado |
|---|---------|-------|--------|--------|
| 1 | **Reportes ampliados**: comparativas por periodo (semana/mes vs anterior), exportar a Excel/CSV y PDF, gráficas de ventas | Alto | Bajo (solo lectura de datos) | PENDIENTE |
| 2 | **Endurecer contraseñas**: hash con sal (p. ej. PBKDF2 de stdlib), migrando los hashes existentes al primer login; forzar cambio de las claves por defecto | Medio | Bajo-medio | PENDIENTE |
| 3 | **Productos a granel (kg/gr)**: vender por peso huevo, jamón, queso, etc. — precio por kg, captura de peso o de monto, stock en decimales | Muy alto (operación diaria real) | Medio-alto (cambia `stock` y `cantidad` de INTEGER a REAL en BD, ticket, corte y reportes) | PENDIENTE |
| 4 | **Multi-equipo / red**: usar el POS desde más de una computadora o sincronizar la base | Alto | Alto (SQLite es archivo local; requiere decidir arquitectura: carpeta compartida con WAL ≠ seguro, o servidor) | PENDIENTE |

## Notas de descubrimiento (Fase 0 del bootstrap, 2026-07-08)

- No hay TODO/FIXME en el código; `MEJORAS.md` histórico es changelog de lo
  ya hecho (login, cortes, apartados, préstamos, mascota, WAL).
- La #3 es la que el dueño más mencionó (huevo, jamón, queso por kg/gr).
  Va después de la #1 y #2 por riesgo: toca esquema de BD y flujo de dinero;
  conviene tener más tests en verde antes de entrarle.
- La #4 probablemente cambie principios de `tech-stack.md` → requiere
  actualizar la constitución en su spec.
- [PENDIENTE] confirmar prioridades con el dueño antes de arrancar la #1.
