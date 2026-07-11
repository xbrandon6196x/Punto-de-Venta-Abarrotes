---
description: "Bucle autónomo: correr tests → diagnosticar → corregir causa raíz → repetir hasta verde (máx. 5 iteraciones)"
argument-hint: "[filtro opcional de pytest]"
allowed-tools: Bash(py -m pytest*), Read, Edit, Grep, Glob
---

Bucle de arreglo con condición de salida objetiva y presupuesto cerrado.

1. Corre `py -m pytest $ARGUMENTS -v`. Si todo está en verde, termina y
   reporta.
2. Si hay fallos, toma UNO (el primero o el más fundamental) y:
   - Lee el test Y el código bajo prueba antes de tocar nada.
   - Identifica la causa raíz. El árbitro es la regla documentada
     (CLAUDE.md, skills, spec) — no el test ni tu intuición.
   - Corrige la causa raíz en el código de producción.
3. Vuelve a correr la suite completa (no solo el test arreglado).
4. Repite. **Presupuesto: 5 iteraciones.** Si al agotarlo sigue en rojo,
   detente y reporta qué falta y qué intentaste.

## PROHIBIDO (romper esto invalida todo el bucle)

- Debilitar tests: borrar asserts, marcar skip/xfail, ampliar tolerancias,
  o cambiar el valor esperado para que coincida con el actual.
- Si concluyes que el TEST está mal (contradice una regla documentada en
  CLAUDE.md/skills/spec): **detente y pregunta** mostrando la regla y el
  conflicto. No "arregles" el test por tu cuenta.
- Tocar la BD real o los archivos de `ando-haciendo-un-proyecto-de-un/`.

## Reporte final

Iteraciones usadas · tests arreglados · archivos tocados (archivo:línea) ·
desviaciones o dudas pendientes.
