# Spec — 002: Endurecer contraseñas

> Estado: APROBADA · Fecha: 2026-07-08

## Qué

Las contraseñas del personal quedarán guardadas de forma segura (con sal,
imposibles de adivinar aunque alguien vea la base de datos o el código en
GitHub). Quien entre con una clave por defecto (admin123, venta123…)
tendrá que elegir una nueva antes de poder usar la caja. Cada usuario
podrá cambiar su propia contraseña desde la app, y el administrador podrá
asignarle una nueva a cualquier usuario si la olvida. La pantalla de
login dejará de mostrar las claves por defecto como pista.

## Por qué

Hoy las contraseñas se guardan con un método débil (SHA-256 sin sal) y
las claves por defecto están publicadas en GitHub y hasta impresas en la
pantalla de login. Cualquiera con acceso a la computadora o al repositorio
puede entrar como administrador a la caja de una tienda real. Además no
existe ninguna forma de cambiar una contraseña sin tocar la base de datos
a mano.

## Alcance

**Incluye:**
- Hash nuevo: PBKDF2-HMAC-SHA256 con sal aleatoria por usuario e
  iteraciones configuradas, todo con la librería estándar (`hashlib`,
  `secrets`) — sin dependencias nuevas. Se guarda en la MISMA columna
  `password_hash` con un formato autodescriptivo
  (`pbkdf2$<iteraciones>$<sal>$<hash>`), sin cambios de esquema.
- **Migración automática al primer login:** los hashes SHA-256 existentes
  de las instalaciones reales siguen funcionando; al iniciar sesión con
  éxito, el hash se actualiza al formato nuevo de forma silenciosa.
- ~~Cambio sugerido con clave por defecto~~ **SUSTITUIDO por la feature
  004 (2026-07-10):** las claves por defecto se eliminaron del código
  (repo público); ya no existe lista contra la cual sugerir. Las
  instalaciones existentes entran con sus claves de siempre sin ningún
  aviso, y las nuevas eligen las suyas en el primer arranque.
- **«Cambiar mi contraseña»:** cualquier usuario puede cambiar la suya
  desde la app (pidiendo la actual).
- **Reseteo por admin:** el administrador puede asignar una contraseña
  nueva a cualquier usuario activo (sin necesitar la anterior).
- Reglas de contraseña nueva: no vacía y distinta de cualquier clave por
  defecto. Sin regla de largo (decisión del dueño: tecleo rápido en caja).
- Quitar del login la pista que muestra las credenciales por defecto.
- Tests: hash con sal (dos usuarios con la misma clave → hashes
  distintos), login legado migra al formato nuevo, detección de clave por
  defecto, cambio y reseteo de contraseña.

**NO incluye (explícito):**
- Cambiar los usuarios iniciales ni impedir que se creen (las tiendas
  existentes los usan; solo se les fuerza clave nueva al entrar).
- Recuperación de contraseña del admin si la olvida (fuera de alcance;
  hoy sería intervención manual, igual que siempre).
- Bloqueo por intentos fallidos, expiración de contraseñas o reglas de
  complejidad (símbolos/mayúsculas).
- Cifrado de la base de datos o de los respaldos.
- Gestión completa de usuarios (crear/desactivar) — solo contraseñas.

## Criterios de aceptación

Verificables uno a uno. El verificador los revisará contra el diff real.

- [ ] Una contraseña nueva se guarda como `pbkdf2$...` con sal aleatoria:
      dos usuarios con la misma contraseña tienen hashes distintos.
- [ ] Un usuario con hash SHA-256 viejo (BD de tienda real) puede entrar
      con su misma contraseña, y tras ese login su hash queda en formato
      `pbkdf2$...` sin que él haga nada.
- [ ] Al entrar con una clave por defecto (p. ej. admin/admin123) la app
      OFRECE elegir contraseña nueva; si el usuario acepta, la nueva no
      puede ser vacía ni otra clave por defecto; si dice que no, entra
      normalmente con su clave de siempre (actualizado 2026-07-10).
- [ ] Tras cambiar la contraseña, el siguiente login con la clave vieja
      falla y con la nueva funciona.
- [ ] Todo usuario tiene a la mano «Cambiar mi contraseña» (pide la
      actual y la nueva); con la actual incorrecta no cambia nada.
- [ ] El admin puede asignar contraseña nueva a cualquier usuario activo
      sin conocer la anterior; ese usuario entra con la nueva.
- [ ] La pantalla de login ya no muestra credenciales por defecto.
- [ ] `py -m pytest` en verde (incluyendo tests nuevos de esta feature).
- [ ] La app arranca (`py pos_abarrotes.py`) y el flujo de login funciona.
- [ ] Una BD existente de la tienda (esquema anterior, hashes viejos)
      abre sin error y sus usuarios pueden entrar (compatibilidad total).
- [ ] Cero cambios de esquema (misma columna `password_hash`).

## Preguntas abiertas

Resolver TODAS antes de pasar a plan.md.

- [x] ¿Forzar cambio con clave por defecto? → Sí, obligatorio al entrar
      (2026-07-08, dueño).
- [x] ¿Quién cambia contraseñas? → cada quien la suya + admin resetea
      (2026-07-08, dueño).
- [x] ¿Regla de largo mínimo? → sin regla de largo; solo no vacía y
      distinta de las claves por defecto (2026-07-08, dueño).
- [x] ¿Pista de credenciales en login? → quitarla (2026-07-08, dueño).
