# Plan — 002: Endurecer contraseñas

> Requiere spec.md APROBADA y sin preguntas abiertas. ✅ (2026-07-08)

## Enfoque

Todo con librería estándar (`hashlib.pbkdf2_hmac`, `secrets`, `hmac`).
El hash nuevo se guarda en la MISMA columna `password_hash` con formato
autodescriptivo `pbkdf2$<iteraciones>$<sal_hex>$<hash_hex>`; un hash
legado se reconoce porque no empieza con `pbkdf2$`. Funciones de lógica
sin UI (testeables con `bd_temporal`):

- `hash_password_pbkdf2(contrasena)` — sal aleatoria de 16 bytes
  (`secrets.token_hex`), `ITERACIONES_PBKDF2 = 600_000` como constante
  (ajustable si la PC de la tienda resultara lenta; <0.5 s típico).
- `verificar_password(contrasena, hash_guardado)` — detecta formato,
  compara con `hmac.compare_digest`; soporta legado SHA-256.
- `es_password_por_defecto(contrasena)` — contra las claves de
  `USUARIOS_INICIALES`.
- `cambiar_password(usuario_id, nueva)` — valida (no vacía, no por
  defecto) y guarda hash nuevo.
- `validar_login` se modifica: usa `verificar_password`; si el hash era
  legado y el login fue exitoso, lo re-escribe en formato nuevo
  (migración silenciosa); el dict devuelto agrega la llave
  `password_por_defecto` (bool) para que la UI dispare el cambio forzado.
- `crear_usuarios_iniciales` pasa a guardar PBKDF2 desde el inicio (la
  detección de clave por defecto es por la contraseña tecleada, no por el
  formato del hash). `hash_password` (SHA-256) se conserva solo para
  verificar hashes legados.

UI: un diálogo único `DialogoCambioContrasena(QDialog)` (QFormLayout +
QDialogButtonBox, patrón del proyecto) con tres usos: **forzado** tras
login con clave por defecto (sin pedir la actual, no se puede saltar:
rechazarlo regresa al login), **voluntario** (pide la actual) y **reseteo
admin** (combo de usuarios activos, sin pedir la actual). Punto de
entrada: botón «🔑 Contraseña» en la statusbar junto a «Cerrar sesión»
(para admin incluye el combo para resetear a otros). El gancho del
forzado va en `pedir_usuario_y_fondo()`, justo tras aceptar el login y
antes del nombre de turno/fondo. La etiqueta de ayuda del login pierde
las credenciales impresas.

**Alternativa descartada:** columnas nuevas `salt`/`algoritmo` en
`usuarios` — obliga migración de esquema y complica el respaldo; el
formato autodescriptivo en la columna existente hace la migración
invisible y reversible. También se descartó bcrypt/argon2 (dependencia
externa, prohibida sin aviso) y scrypt (más memoria en PCs modestas de
tienda); PBKDF2 es el estándar disponible en stdlib.

## Archivos / secciones afectadas

| Archivo · sección | Cambio |
|-------------------|--------|
| `pos_abarrotes.py` · imports | añadir `hmac`, `secrets` (stdlib) |
| `pos_abarrotes.py` · configuración | constante `ITERACIONES_PBKDF2` |
| `pos_abarrotes.py` · funciones de BD/validadores | nuevas `hash_password_pbkdf2`, `verificar_password`, `es_password_por_defecto`, `cambiar_password`; modificar `validar_login` y `crear_usuarios_iniciales` |
| `pos_abarrotes.py` · diálogos | nuevo `DialogoCambioContrasena`; `DialogoLogin` pierde la pista de credenciales |
| `pos_abarrotes.py` · `pedir_usuario_y_fondo` | gancho del cambio forzado tras login |
| `pos_abarrotes.py` · `POSAbarrotes.__init__` (statusbar) | botón «🔑 Contraseña» |
| `tests/test_contrasenas.py` (nuevo) | formato/sal, verificación legado, migración al login, clave por defecto, cambiar/resetear, usuarios iniciales en PBKDF2 |

## Datos / estado nuevos

**Ninguna columna ni tabla nueva.** Solo cambia el CONTENIDO de
`password_hash` (formato `pbkdf2$...`), y únicamente al iniciar sesión o
cambiar la contraseña. Esquema intacto → BDs viejas abren sin paso manual.

## Impacto por capa

- **BD:** sin migraciones; `UPDATE usuarios SET password_hash` en login
  exitoso legado y en cambios de contraseña.
- **Lógica de negocio:** solo autenticación; ventas/caja/reportes
  intactos.
- **UI:** diálogo nuevo, botón en statusbar, gancho en el flujo de
  entrada, texto del login.
- **Reportes / corte de caja:** sin impacto (la atribución usa
  `vendedor_nombre`, que no cambia).

## Riesgos

- **Instalación real no puede entrar tras actualizar** → la verificación
  legada se prueba con un hash SHA-256 sembrado; criterio de aceptación
  dedicado. El formato viejo sigue aceptándose para siempre (solo se
  migra, nunca se rechaza).
- **Login lento en PC vieja** (600k iteraciones) → constante única
  ajustable; se mide en el humo. El costo ocurre solo al entrar, no
  durante la venta.
- **Usuario cierra el diálogo forzado** → regresa al login (no queda a
  medias dentro de la app con clave débil).
- **Admin se resetea a sí mismo por accidente** → el reseteo a uno mismo
  exige la contraseña actual (usa el modo voluntario).
- **Tests existentes** (`test_hash_password_es_determinista_y_distingue`,
  `test_login_con_usuarios_iniciales`) → siguen válidos: `hash_password`
  se conserva y `validar_login` solo AGREGA una llave al dict.
