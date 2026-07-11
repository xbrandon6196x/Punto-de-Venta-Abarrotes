---
description: "Checklist pre-publicación: tests, dependencias, config, git limpio y escaneo de secretos (bloqueante)"
allowed-tools: Bash, Read, Grep, Glob
---

Checklist antes de subir a GitHub o de generar un `.exe` para la tienda.
Ejecuta TODO y presenta la tabla final; cualquier ❌ bloquea la publicación.

1. **Tests** — `py -m pytest`: todo en verde.
2. **Arranque** — `py -c "import pos_abarrotes"` sin traceback.
3. **Sin dependencias sorpresa** — los imports de `pos_abarrotes.py` solo
   pueden requerir PySide6 + stdlib; `tests/` puede añadir pytest. Compara
   contra `requirements.txt`.
4. **Config correcta** — `DB_NAME` sigue siendo `"abarrotes_pos.db"` (ruta
   relativa) y no quedó apuntando a ninguna BD de prueba.
5. **Git limpio** — `git status`: sin archivos sin trackear inesperados;
   verificar con `git check-ignore` que `*.db`, `*.exe`, `build/`, `dist/`,
   `__pycache__/` y `.claude/settings.local.json` siguen ignorados.
6. **Escaneo de secretos (BLOQUEANTE)** — sobre los archivos trackeados
   (`git ls-files`) y el diff a subir:
   - `git ls-files` no debe contener `.db`, `.exe`, `.env*`, `.pem`, `.key`.
   - Grep de patrones: `api[_-]?key`, `token`, `password\s*=`, `Bearer `,
     `AKIA`, `sk-`, cadenas base64 largas. Las contraseñas por defecto de
     `USUARIOS_INICIALES` son conocidas y públicas: reporta si aparece
     cualquier OTRA credencial.
   - Si encuentras algo: **DETENTE**, repórtalo y no publiques. Recuerda
     que borrar el archivo en un commit nuevo NO lo saca del historial.
7. **Datos reales** — confirmar que ningún archivo a subir contiene datos
   de ventas/clientes reales de la tienda.

Formato del reporte: tabla `| Chequeo | ✅/❌ | Detalle |` + veredicto
final: PUBLICABLE / BLOQUEADO (con razones).
