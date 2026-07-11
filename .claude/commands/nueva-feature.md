---
description: "Ciclo SDD completo para una feature: Specify → Plan → Tasks → Implement → Verify, con OK humano entre fases"
argument-hint: "<nombre corto de la feature, ej. productos-a-granel>"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Agent
---

Ciclo spec-anchored. La spec es la fuente de verdad: si la implementación
se desvía del «qué», se actualiza la spec ANTES de seguir programando.

## 1. Specify

1. Determina el número: mira `spec/features/` y usa el siguiente NNN
   (la 000 es plantilla). Crea `spec/features/NNN-$ARGUMENTS/`.
2. Copia `spec/features/000-plantilla/spec.md` y rellénala CON el usuario:
   qué (visión de usuario, sin tecnicismos), por qué, alcance (incluye /
   NO incluye explícito), criterios de aceptación verificables uno a uno
   (siempre incluir: `py -m pytest` en verde + la app arranca + la BD
   existente de la tienda sigue abriendo), preguntas abiertas.
3. Resuelve TODAS las preguntas abiertas con el usuario antes de seguir.
4. **Espera OK del usuario sobre la spec.**

## 2. Plan

5. Copia y rellena `plan.md`: enfoque elegido (y la alternativa
   descartada, con motivo), tabla de archivos/secciones afectadas de
   `pos_abarrotes.py`, columnas/tablas nuevas (recuerda: migraciones solo
   aditivas — skill esquema-bd), impacto por capa (BD / lógica / UI /
   reportes / corte de caja), riesgos.
6. **Espera OK del usuario sobre el plan.**

## 3. Tasks

7. Copia y rellena `tasks.md`: tareas pequeñas y verificables que dejan la
   app funcionando tras CADA una; las últimas siempre son «tests de la
   feature pasan» y «criterios de aceptación verificados uno a uno».

## 4. Implement

8. Ejecuta las tareas en orden, marcando el checklist y anotando fechas y
   desviaciones en la sección «Registro» de tasks.md.
9. Si hay **3+ tareas independientes entre sí**, delega cada una al
   subagente `implementador` (una tarea por invocación, con la ruta de la
   spec y la tarea exacta). Si son secuenciales, hazlas tú en la sesión.
10. Si una desviación cambia el «qué» de la spec: PARA, actualiza spec.md,
    pide OK y continúa.

## 5. Verify

11. Lanza el subagente `verificador` con: ruta de la spec, diff real
    (`git diff`), y la instrucción de validar los criterios uno a uno.
12. Si el veredicto es RECHAZADO o CON RESERVAS: corrige y repite la
    verificación (máx. 3 ciclos; después, escala al usuario).
13. Con APROBADO: actualiza el estado de la feature en
    `spec/constitution/roadmap.md`, resume al usuario y ofrece commit
    (sin push sin permiso).
