---
description: Escribe la bitácora de la sesión en docs/sesiones/ y sincroniza roadmap/tasks si una feature avanzó
allowed-tools: Read, Write, Edit, Bash(git status*), Bash(git diff*), Bash(git log*), Glob, Grep
---

1. Determina el número de bitácora: mira `docs/sesiones/` y usa el
   siguiente NNN (la 000 es plantilla). Nombre:
   `docs/sesiones/NNN-AAAA-MM-DD-tema.md`.
2. Rellena la plantilla `docs/sesiones/000-plantilla.md` leyendo la
   conversación REAL de esta sesión y el estado REAL del repo
   (`git status`, `git log --oneline -5`, `py -m pytest` si aplica):
   - **Qué se hizo**: con archivos tocados (archivo:línea si ayuda).
   - **Decisiones**: SOLO las que no están ya en spec/CLAUDE.md — si una
     decisión pertenece a la spec o a CLAUDE.md, escríbela ALLÁ y aquí
     solo enlázala. No dupliques.
   - **Pendiente / siguiente paso**: lo primero que debe hacer la próxima
     sesión, concreto y accionable.
   - **Estado del repo**: rama, cambios sin commitear, resultado de tests.
3. Si una feature avanzó en esta sesión: actualiza su `tasks.md` (checklist
   y Registro) y el estado en `spec/constitution/roadmap.md`.
4. Muestra la bitácora al usuario y recuérdale que ya puede usar `/clear`
   con seguridad (la memoria quedó en disco).
