---
description: Corre los tests del POS y reporta el resultado; si fallan, diagnostica pero NO arregla sin OK
argument-hint: "[ruta o filtro opcional, ej. tests/test_logica.py -k caja]"
allowed-tools: Bash(py -m pytest*), Read, Grep, Glob
---

1. Corre los tests reales: `py -m pytest $ARGUMENTS -v` (si no hay
   argumentos, corre toda la suite `py -m pytest -v`).
2. Reporta: cuántos pasaron/fallaron/se saltaron y el tiempo.
3. Si TODO pasa: termina con un resumen de una línea. No toques nada.
4. Si algo falla:
   - Lee el traceback completo y el test que falla.
   - Diagnostica la causa raíz (¿el test está desactualizado o el código
     tiene un bug?) citando archivo:línea.
   - Presenta el diagnóstico y la corrección propuesta. **NO apliques
     ninguna corrección sin OK explícito del usuario** (para el bucle
     autónomo de arreglo está `/arregla-tests`).
5. Recordatorio permanente: los tests usan BD temporal; si un test
   intenta tocar `abarrotes_pos.db` real, eso ES el bug — repórtalo.
