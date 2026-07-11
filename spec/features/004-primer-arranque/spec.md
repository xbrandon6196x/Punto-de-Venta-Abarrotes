# Spec — 004: Primer arranque sin claves en el código

> Estado: APROBADA · Fecha: 2026-07-10 (aprobada por el dueño junto con
> el plan de publicación a GitHub)

## Qué

El código publicado en GitHub ya no contiene ninguna contraseña. La
primera vez que el sistema se abre con una base de datos nueva, aparece
una pantalla de bienvenida donde el dueño elige las contraseñas de la
cuenta de administrador («admin») y de la cuenta de caja («vendedor»).
Las tiendas que ya están funcionando no notan ningún cambio: sus
usuarios y claves viven en su base de datos y siguen entrando igual.

## Por qué

El repositorio es público y las claves por defecto (`admin123`,
`venta123`…) estaban escritas en el código fuente: cualquiera podía
leerlas. El dueño pidió publicar el proyecto SIN contraseñas — que cada
instalación use las que elija el usuario.

## Alcance

**Incluye:**
- `DialogoPrimerUsuario` al arrancar con BD sin usuarios activos: crea
  «admin» y «vendedor» con claves elegidas (confirmación doble, no
  vacías, distintas entre sí). Cancelarlo cierra la app (sin cuentas no
  hay quién entre).
- Eliminación de `USUARIOS_INICIALES` y de toda clave en el fuente;
  `crear_usuario()` y `hay_usuarios_activos()` como helpers.
- Desaparece la «invitación a cambiar clave por defecto» de la 002 (ya
  no existe lista de claves por defecto); el botón «🔑 Contraseña» sigue
  siendo la vía para cambios y reseteos.
- `cambiar_password` pierde la regla «no clave por defecto» (sin lista
  no hay regla); queda: no vacía.
- Tests con claves ficticias de prueba sembradas por el conftest, y un
  test guardián que verifica que las claves históricas NO aparezcan en
  el fuente.

**NO incluye (explícito):**
- Gestión completa de usuarios (crear más cuentas, desactivar) — los
  perfiles extra (`vendedor1..3`) de instalaciones viejas siguen en su
  BD, pero las instalaciones nuevas nacen solo con admin + vendedor.
- Cambiar nada en la BD de la tienda real.
- Limpieza del historial de git (va en el plan de publicación, no aquí).

## Criterios de aceptación

- [x] Con BD nueva, la app pide crear las dos cuentas antes del login;
      cancelar cierra la app.
- [x] Las claves elegidas quedan con hash PBKDF2 y sirven para entrar.
- [x] `admin123`/`venta123`/`venta456`/`venta789` no existen en
      `pos_abarrotes.py` (test guardián `test_codigo_sin_claves_quemadas`).
- [x] Una BD existente (con usuarios) NO muestra el diálogo y sus
      usuarios entran igual que siempre.
- [x] `py -m pytest` en verde (40 tests).
- [x] La app arranca y el flujo tocado funciona.

## Preguntas abiertas

- [x] ¿Publicar sin claves y con primer arranque? → Sí (2026-07-10,
      dueño, al aprobar el plan de push).
