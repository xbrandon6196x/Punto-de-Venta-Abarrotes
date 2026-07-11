# Checklist de seguridad — POS Tienda Periquita

Contexto de riesgo real: repo alojado en GitHub (trátalo como **público**),
la app maneja **dinero e inventario reales** de la tienda y la BD contiene
**datos de clientes** (nombres, teléfonos, correos, deudas). No hay backend
ni servicios en la nube: el riesgo vive en el repo y en la máquina de la tienda.

## Los 4 principios (adaptados a este proyecto)

1. **Contexto + seguridad por adelantado.** Antes de pedir trabajo a la IA,
   el arnés ya carga CLAUDE.md y skills con las reglas (BD real intocable,
   migraciones aditivas, corte de caja). No empezar tareas de dinero/esquema
   sin pasar por `/nueva-feature`.
2. **Leer y entender el diff ENTERO antes de aprobar.** Especialmente todo
   lo que toque `resumen_caja_sesion`, stock, precios o `crear_tablas()`.
   Si no entiendes una línea del diff, pregunta antes del OK.
3. **Verificar antes de subir.** `/deploy-check` SIEMPRE antes de push o de
   generar un `.exe` para la tienda: tests en verde + escaneo de secretos
   bloqueante + `git status` limpio.
4. **Nunca pegar datos reales en un prompt.** Ni la BD, ni ventas, ni
   teléfonos de clientes, ni contraseñas nuevas. Para depurar, generar
   datos falsos en una BD temporal (los tests ya lo hacen así).

## Tabla de amenazas reales

| Amenaza | Impacto | Mitigación |
|---------|---------|------------|
| Commitear la BD real (`abarrotes_pos.db`) al repo público | Datos de clientes y ventas expuestos | `*.db` en `.gitignore` (verificado con `git check-ignore`) + escaneo bloqueante en `/deploy-check` |
| **BDs y `.exe` reales ya en el HISTORIAL de git** (commit "Primera version POS") | Quien clone el repo puede extraerlos aunque ya no estén en HEAD | RESUELTO 2026-07-10: historial local reescrito sin ese commit + force-push; el repo de GitHub se vuelve privado porque la plataforma puede retener commits viejos por SHA |
| Contraseñas por defecto hardcodeadas en el código publicado (el personal de la tienda las sigue usando) | Cualquiera que lea el repo entra como admin al POS | RESUELTO 2026-07-10 (feature 004): las claves se eliminaron del fuente, docs y tests; cada instalación crea las suyas en el primer arranque. Defensa extra: repo privado. Las claves reales de la tienda solo existen como hash en su BD local |
| Hash SHA-256 sin sal en `usuarios.password_hash` | Hashes filtrados se revierten con tablas rainbow | RESUELTO (feature 002): PBKDF2 con sal de stdlib; hashes legados migran solos al primer login |
| La IA corre tests/scripts contra la BD real y corrompe ventas | Pérdida de datos del negocio | Regla dura en CLAUDE.md + tests con BD temporal + respaldo automático `abarrotes_pos_respaldo.db` |
| Migración destructiva rompe la BD de la tienda al actualizar el `.exe` | La tienda no puede cobrar | Solo `agregar_columna_si_falta()` (skill esquema-bd) + criterio fijo en toda spec: "BD anterior abre sin error" |
| Dependencia nueva maliciosa/frágil entra al `.exe` | Código no auditado corriendo en la caja | Regla "sin dependencias nuevas sin avisar" + chequeo de imports en `/deploy-check` |
| Pérdida de la máquina de la tienda (robo/falla de disco) | Pérdida total de datos | [PENDIENTE] definir respaldo EXTERNO periódico de `abarrotes_pos.db` (USB/nube cifrada); el respaldo automático vive en el mismo disco |

## Reglas de oro

- `.env*`, `*.pem`, `*.key`, `*.db`, `*.exe`, `.claude/settings.local.json`
  jamás se commitean (ya en `.gitignore`).
- Si algún día se usa una API key (p. ej. en `.mcp.json`): variable de
  entorno `${VAR}`, nunca el valor en el archivo.
- Un secreto que llegó a un commit se considera QUEMADO: rotarlo, no solo
  borrarlo.
