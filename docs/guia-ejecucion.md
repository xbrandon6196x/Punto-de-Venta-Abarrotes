# Guía de ejecución — qué modo usar y cuándo

## Modos de trabajo

| Situación | Modo |
|-----------|------|
| Feature del roadmap (nueva capacidad, toca BD/dinero/UI) | `/nueva-feature` (ciclo SDD completo con OKs) |
| Refactor, zona crítica (corte de caja, `crear_tablas`, migraciones) | **Plan Mode** primero: plan revisado y aprobado antes de editar |
| Cambio atómico y verificable (un texto, un color, un mensaje, un test) | **Build** directo: pedirlo y revisar el diff |
| Tests rotos | `/test` para diagnóstico · `/arregla-tests` para el bucle de arreglo |
| Antes de subir a GitHub o generar `.exe` | `/deploy-check` |
| Terminar la jornada | `/cierre-sesion` |

Regla del flujo estricto (elegida en el bootstrap): toda tarea no trivial
lleva plan + OK del dueño antes de editar.

## Subagentes: cuándo sí y cuándo no

- **Sí** — `implementador` (model: sonnet): 3+ tareas independientes de un
  `tasks.md`; cada invocación = UNA tarea con su spec.
- **Sí, siempre** — `verificador`: fase Verify de toda feature y antes de
  commits importantes. No puede editar: su veredicto es independiente.
- **Sí** — subagente Explore para búsquedas amplias en `pos_abarrotes.py`
  (7,000 líneas): "¿dónde se toca stock?" — devuelve conclusiones sin
  quemar contexto de la sesión principal.
- **No** — para cambios pequeños: un subagente arranca SIN contexto
  (no vio tu conversación); explicárselo cuesta más que hacerlo en la
  sesión. Lo barato para lo chico es la sesión principal.

## Higiene de contexto

- Preferir `/compact` **dirigible** («/compact conserva la spec de granel y
  el estado de tasks») en vez de `/clear`.
- `/clear` SOLO después de `/cierre-sesion` (la memoria ya quedó en disco).
- Referenciar rutas (`spec/features/003-*/spec.md`) en vez de pegar
  archivos completos al chat.
- Al retomar: bitácora más reciente de `docs/sesiones/` + roadmap. No
  reconstruir de memoria lo que ya está escrito.

## Loop engineering (bucles autónomos)

Un bucle autónomo bien formado tiene SIEMPRE tres piezas:

1. **Acción verificable** — p. ej. correr `py -m pytest` y corregir la
   causa raíz del primer fallo.
2. **Condición de salida objetiva** — suite en verde; no "se ve bien".
3. **Presupuesto de iteraciones** — `/arregla-tests` usa 5; al agotarlo se
   detiene y reporta, no insiste a ciegas.

**El árbitro es la regla documentada, no el test.** Si el bucle descubre
que un test contradice CLAUDE.md/skills/spec, se detiene y pregunta:
"arreglar" el test para que pase es la forma más rápida de romper el corte
de caja sin que nadie lo note.
