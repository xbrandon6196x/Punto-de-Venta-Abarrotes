# Tasks — 004: Primer arranque sin claves en el código

> Feature ejecutada completa el 2026-07-10 como requisito del plan de
> publicación a GitHub aprobado por el dueño.

## Checklist

- [x] T1. Eliminar `USUARIOS_INICIALES` y toda clave del fuente;
      helpers `crear_usuario()` y `hay_usuarios_activos()`.
- [x] T2. `DialogoPrimerUsuario` (admin + vendedor, confirmación doble,
      claves distintas entre sí) + gancho en `__main__`.
- [x] T3. Retirar el flujo «sugerido» de la 002 (sin lista de claves no
      hay sugerencia); `cambiar_password` solo exige no vacía.
- [x] T4. Tests: conftest siembra usuarios de prueba; guardián
      `test_codigo_sin_claves_quemadas` (claves invertidas); BD nueva no
      siembra usuarios; crear_usuario + login. Suite: 40 en verde.
- [x] T5. Saneamiento de claves históricas en docs/specs/tests
      (bloqueo de /deploy-check) — commit `c954c29`.
- [x] T6. Verificación: humo headless del diálogo (confirmaciones,
      claves iguales, creación real) + exe probado con BD nueva
      (muestra el primer arranque) y con copia de la BD real (no lo
      muestra; usuarios intactos).

## Registro

| Fecha | Tarea | Nota |
|-------|-------|------|
| 2026-07-10 | T1–T6 | Ejecutada en la sesión de publicación (bitácora `docs/sesiones/002-*`). Sin verificador subagente dedicado: la validó /deploy-check (bloqueante) + humos + 40 tests; el riesgo residual es bajo (sin cambios de esquema ni de dinero). |
