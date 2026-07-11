# Tasks — 002: Endurecer contraseñas

> Cada tarea es pequeña, verificable, y deja la app FUNCIONANDO al
> terminarla (no hay tareas que rompan y "luego se arregla").

## Checklist

- [x] T1. Lógica sin UI: `ITERACIONES_PBKDF2`, `hash_password_pbkdf2`,
      `verificar_password` (PBKDF2 + legado SHA-256),
      `es_password_por_defecto`, `cambiar_password`; `validar_login`
      migra hashes legados y devuelve `password_por_defecto`;
      `crear_usuarios_iniciales` guarda PBKDF2. Verificar: pytest verde
      y app arranca.
- [x] T2. Tests en `tests/test_contrasenas.py`: sal distinta con misma
      clave, verificación y migración de hash legado, detección de clave
      por defecto, cambiar/resetear contraseña, usuarios iniciales en
      formato nuevo. Verificar: `py -m pytest` en verde.
- [x] T3. `DialogoCambioContrasena` (forzado / voluntario / reseteo
      admin) + quitar credenciales de la pista del login. Verificar: app
      arranca, diálogo abre en los tres modos.
- [x] T4. Gancho de cambio forzado en `pedir_usuario_y_fondo` + botón
      «🔑 Contraseña» en la statusbar. Verificar: humo headless — login
      con clave por defecto exige cambio; rechazar el diálogo no entra;
      con clave nueva entra directo.
- [x] T5. Tests de la feature pasan: `py -m pytest` en verde completo (31).
- [x] T6. Criterios de aceptación de spec.md verificados uno a uno
      (subagente verificador sobre `git diff`): **APROBADO**, 10/11
      CUMPLE + 1 con evidencia indirecta (arranque GUI, humo documentado).

## Registro

Anotar fechas, desviaciones y decisiones tomadas durante la implementación.
**Si una desviación cambia el «qué» → actualizar spec.md ANTES de seguir.**

| Fecha | Tarea | Nota |
|-------|-------|------|
| 2026-07-08 | — | Spec y plan aprobados por el dueño; arranca implementación. |
| 2026-07-08 | T1–T2 | Lógica PBKDF2 + 8 tests; conftest baja iteraciones en tests (misma lógica, sin costo). |
| 2026-07-09 | T3–T5 | Diálogo con 3 modos + gancho + botón statusbar. Humo headless: 7 escenarios OK; login real con 600k iteraciones = 0.41 s; 31 tests en verde; app arranca. |
| 2026-07-10 | post | Decisión del dueño: el cambio de contraseña con clave por defecto pasa de OBLIGATORIO a SUGERIDO (el personal ya se aprendió las claves). spec.md actualizada antes del código; modo del diálogo renombrado a "sugerido"; cancelar deja pasar. Riesgo aceptado y anotado: las claves por defecto siguen activas mientras el repo de GitHub no se limpie/privatice. |
| 2026-07-09 | T6 | Verificador: APROBADO. Sin bypass del forzado (ambas rutas pasan por pedir_usuario_y_fondo), compare_digest en ambas ramas, hashes malformados fallan cerrado. Hallazgos menores anotados: timing de enumeración de usuarios (preexistente), cambiar_password no valida usuario_id inexistente, _inp_actual sin layout en modo forzado (cosmético). |
