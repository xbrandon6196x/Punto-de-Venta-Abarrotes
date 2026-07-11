# Stack normativo

## Stack (lo que se usa y por qué)

| Capa | Tecnología | Nota normativa |
|------|-----------|----------------|
| Lenguaje | Python 3.13 | En esta máquina se invoca `py` (no `python`) |
| UI | PySide6 (Qt) | Única dependencia de runtime; tema Catppuccin Mocha vía `ESTILO` |
| Datos | SQLite (stdlib `sqlite3`) | Modo WAL, `foreign_keys=ON`, respaldo automático |
| Tests | pytest | Sobre BD temporal, nunca la real |
| Empaquetado | PyInstaller | `--onefile --noconsole`; el `.exe` NO se commitea |
| CI/CD | Ninguno | [PENDIENTE] valorar GitHub Actions para correr pytest |

## Arquitectura con reglas duras

1. **Un solo archivo**: toda la app vive en `pos_abarrotes.py`. Es una
   decisión deliberada (fácil de empaquetar y copiar a la tienda). NO se
   divide en módulos sin decisión explícita del dueño.
2. **Orden interno del archivo** (respetarlo al insertar código):
   configuración → `ESTILO` → funciones de BD → validadores → casillas y
   mixins → diálogos → mascota → pestañas/ventana principal → `main`.
3. **BD junto al programa**: `DB_NAME` es ruta relativa; el `.exe` y el
   `.py` crean/abren la BD en su carpeta. No convertir a ruta absoluta ni
   a config externa sin spec.
4. **Migraciones solo aditivas** con `agregar_columna_si_falta()` (ver
   skill `esquema-bd`). Compatibilidad hacia atrás obligatoria: hay BDs
   reales en producción.
5. **Sin dependencias nuevas** sin aprobación explícita (afectan el tamaño
   y fragilidad del `.exe`).
6. **Acceso a BD siempre vía `conectar()`** — nunca `sqlite3.connect`
   directo en código nuevo (excepto los tests y el respaldo interno).
