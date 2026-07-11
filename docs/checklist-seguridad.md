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
| **BDs y `.exe` reales ya en el HISTORIAL de git** (commit "Primera version POS") | Quien clone el repo puede extraerlos aunque ya no estén en HEAD | ⚠️ ABIERTO: decidir entre reescribir historial (`git filter-repo`) + force-push, o hacer el repo privado. Borrarlos en un commit nuevo NO basta |
| Contraseñas por defecto (`admin/admin123`, `vendedor/venta123`) publicadas en README y hardcodeadas en `USUARIOS_INICIALES` | Cualquiera con acceso físico al POS entra como admin | Feature #2 del roadmap: forzar cambio en primer uso + hash con sal. Mientras tanto: cambiar las claves en la instalación real de la tienda |
| Hash SHA-256 sin sal en `usuarios.password_hash` | Hashes filtrados se revierten con tablas rainbow | Feature #2 del roadmap (PBKDF2 de stdlib, sin dependencias nuevas) |
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
