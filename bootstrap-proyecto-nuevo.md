# BOOTSTRAP — Infraestructura de trabajo con IA para un proyecto

> **Cómo usar este documento (humano):** copia este archivo a la raíz del
> otro proyecto y dile a Claude Code:
> *«Lee `bootstrap-proyecto-nuevo.md` y ejecútalo fase por fase.»*
> Eso es todo. El documento contiene las instrucciones y las plantillas.

---

## Instrucciones para el agente que ejecuta este bootstrap

Eres el responsable de montar la infraestructura de trabajo con IA de este
proyecto (arnés + SDD + memoria + verificación + seguridad). Reglas de
ejecución:

1. **Adapta, no copies.** Todo lo que generes debe reflejar el stack, los
   comandos y las convenciones REALES de este repo (detectados en Fase 0),
   no los ejemplos de las plantillas.
2. **No inventes.** Lo que no puedas deducir del repo, pregúntalo. Lo que
   el usuario no sepa aún, déjalo marcado `[PENDIENTE]`.
3. **No destruyas.** Si un archivo ya existe (CLAUDE.md, .gitignore,
   .mcp.json…), muéstrale al usuario qué añadirías/cambiarías y espera OK.
4. **Idioma:** pregunta en qué idioma quiere la documentación y úsalo en
   todo (este bootstrap asume español).
5. Ejecuta las fases EN ORDEN y confirma con el usuario al final de cada
   una. Al terminar, verifica contra el manifiesto final.

**La mentalidad que todo esto implementa** (inclúyela en la documentación
que generes): el humano dirige, la IA ejecuta; el humano es el responsable
final y Validador de Intentos. La potencia sin control no sirve de nada.

---

## Fase 0 — Reconocimiento y decisiones

1. **Detecta del repo:** lenguaje(s), framework/runtime, gestor de paquetes,
   comandos reales (dev, test, lint, build — búscalos en package.json,
   Makefile, README, CI), estructura de carpetas, si hay tests y cómo
   corren, si hay CI/CD, y si el repo es público o privado.
2. **Pregunta al usuario** (usa opciones cerradas):
   - ¿Idioma de la documentación?
   - ¿Flujo estricto (plan + OK antes de toda tarea no trivial) o ligero
     (OK solo para cambios grandes)?
   - ¿Nivel SDD? Recomienda **spec-anchored** (la spec se mantiene viva).
   - ¿Qué features vienen? (para el roadmap; ofrece detectar TODOs/issues)
   - ¿El agente puede probar lo que construye? (¿cómo se corren los tests
     aquí?) Si no hay forma, propón crearla ANTES de seguir — sin
     verificación no hay bucle autónomo.

---

## Fase 1 — CLAUDE.md (las reglas del proyecto)

Crea `CLAUDE.md` en la raíz (**máx. 500 líneas**; si el proyecto también
usa otros agentes, crea `AGENTS.md` con el mismo contenido). Estructura:

```markdown
# [Nombre del proyecto]
[1–2 frases: qué es y para quién.]

## Stack
- Lenguaje / framework / BD / tests / despliegue  [lo DETECTADO, real]

## Comandos
- `[dev]` — arranca en local
- `[test]` — tests (deben pasar antes de cada commit)
- `[lint]` / `[build]` — si existen; si no, dilo explícitamente

## Estructura del proyecto
- `[carpeta]/` — [responsabilidad + regla dura si la hay]

## Convenciones
- [nombres, dónde van los tests, manejo de errores, patrones]
- [invariantes del dominio que ningún cambio debe romper]

## No hagas
- [sin dependencias nuevas sin avisar / zonas congeladas / anti-patrones]
- No commitees secretos ni config personal ([ajustar a si es repo público])

## Flujo de trabajo
- Spec-anchored (SDD): features pasan por spec/features/NNN (usar /nueva-feature).
- [Estricto o ligero, según Fase 0.]
- Si no estás seguro al 80%, pregunta. No inventes.
- Al retomar: leer docs/sesiones/ más reciente + roadmap. Al cerrar: /cierre-sesion.

## Documentación
- [enlaces a README, spec/, docs/, skills, comandos — se completa en Fase 7]
```

---

## Fase 2 — Arnés: MCP, Skills y Comandos

### 2a. MCP Context7

Crea `.mcp.json` en la raíz (transporte HTTP: no requiere Node/npx):

```json
{ "mcpServers": { "context7": { "type": "http", "url": "https://mcp.context7.com/mcp" } } }
```

Si necesita API key algún día: `${VARIABLE_DE_ENTORNO}`, nunca en el archivo.
Añade otros MCP solo si el usuario los pide.

### 2b. Skills (conocimiento que se carga solo)

Crea 1–3 skills en `.claude/skills/<nombre>/SKILL.md` para los **dominios
calientes** del repo (donde hay reglas que un agente violaría sin saberlo:
esquemas de datos, convenciones visuales, reglas de negocio). Formato:

```markdown
---
name: <kebab-case>
description: Usar siempre que [disparadores concretos: archivos, temas].
---
# [Dominio]
[Esquemas EXACTOS, rangos válidos, reglas con sus porqués, qué verificar
después de editar. Datos reales del repo, no genéricos.]
```

### 2c. Comandos (acciones que invoca el humano)

Crea en `.claude/commands/` (formato: frontmatter `description`,
`argument-hint`, `allowed-tools` + instrucciones paso a paso numeradas):

| Comando | Qué hace |
|---------|----------|
| `/test` (o el nombre natural aquí) | Corre los tests reales y reporta; si fallan, diagnostica pero NO arregla sin OK |
| `/arregla-tests` | Bucle: correr → diagnosticar → corregir causa raíz → repetir. Salida: todo verde. Presupuesto: 5 iteraciones. PROHIBIDO debilitar tests; si el test contradice la regla documentada, parar y preguntar |
| `/nueva-feature` | El ciclo SDD completo (ver Fase 3): crea spec/features/NNN desde la plantilla y guía Specify→Plan→Tasks→Implement→Verify con OK humano entre fases |
| `/deploy-check` | Checklist pre-publicación: tests ✅, sin dependencias sorpresa, config correcta, `git status` limpio, **escaneo de secretos bloqueante** |
| `/cierre-sesion` | Escribe la bitácora en docs/sesiones/ (ver Fase 5) |
| `/nueva-<entidad>` | SOLO si el repo tiene una entidad que se añade a menudo (cartas, endpoints, migraciones…): alta guiada con validación |

---

## Fase 3 — SDD: la spec como ancla de verdad

Crea esta estructura:

```
spec/
├── constitution/
│   ├── mission.md      ← qué se construye, para quién, principios
│   │                     innegociables y qué NO es el proyecto
│   ├── tech-stack.md   ← stack normativo + arquitectura con reglas duras
│   └── roadmap.md      ← features de Fase 0, ordenadas por riesgo/valor
│                         (menor riesgo primero); estado por feature
└── features/
    └── 000-plantilla/
        ├── spec.md
        ├── plan.md
        └── tasks.md
```

**Plantilla `spec.md`:** Qué (visión usuario, sin tecnicismos) · Por qué ·
Alcance (incluye / NO incluye explícito) · **Criterios de aceptación**
verificables uno a uno (incluye siempre: tests pasan + sin regresiones
propias del proyecto) · Preguntas abiertas (resolver ANTES de plan).

**Plantilla `plan.md`:** Enfoque (y alternativa descartada) · Archivos
afectados (tabla) · Datos/estado nuevos · Impacto por capa · Riesgos.

**Plantilla `tasks.md`:** checklist de tareas pequeñas y verificables que
dejan el proyecto funcionando tras cada una, terminando en tests +
verificación de criterios · sección «Registro» para fechas y desviaciones
(si una desviación cambia el «qué» → actualizar spec.md antes de seguir).

---

## Fase 4 — Multiagentes

Crea en `.claude/agents/`:

**`implementador.md`** — frontmatter: `tools: Read, Edit, Write, Grep,
Glob, Bash` + **`model: sonnet`** (tarea acotada = modelo medio). Cuerpo:
ejecuta UNA tarea de un tasks.md; no replanifica, no amplía alcance, no
hace commits; lee los archivos antes de editarlos e imita el estilo; si la
tarea es imposible, se detiene y reporta. Reporte: tarea, estado, archivos
tocados, verificación, desviaciones.

**`verificador.md`** — frontmatter: `tools: Read, Grep, Glob, Bash`
(**sin herramientas de edición — es su garantía de independencia**) y SIN
`model:` (hereda el potente: la verificación es el freno del coche, ahí no
se ahorra). Cuerpo: revisor escéptico; revisa el diff real, corre los
tests, valida criterios uno a uno, vigila las violaciones típicas del repo
(sácalas del CLAUDE.md). Veredicto: APROBADO / RECHAZADO / CON RESERVAS,
con evidencia archivo:línea.

El coordinador es la sesión principal (no se define aparte). Conecta ambos
al `/nueva-feature`: implementador para 3+ tareas independientes,
verificador siempre en la fase Verify.

---

## Fase 5 — Memoria y contexto

1. Crea `docs/sesiones/000-plantilla.md`: Qué se hizo (con archivos) ·
   Decisiones (solo las que NO están ya en spec/CLAUDE.md — enlaza, no
   dupliques) · Pendiente/siguiente paso · Estado del repo (rama, sin
   commitear, tests).
2. El comando `/cierre-sesion` (Fase 2c) la rellena leyendo la conversación
   y el `git status` real, y sincroniza roadmap/tasks si una feature avanzó.
3. Documenta en `docs/` la regla: `/compact` (dirigible: «/compact conserva
   X») en vez de `/clear`; `/clear` solo tras `/cierre-sesion`; búsquedas
   amplias → subagente Explore; referenciar rutas en vez de pegar archivos.

---

## Fase 6 — Seguridad (transversal)

1. **`.gitignore`** — si no existe créalo; asegura como mínimo: `.env*`,
   `*.pem`, `*.key`, `.claude/settings.local.json`, artefactos de build y
   basura de SO. Verifica con `git check-ignore`.
2. **Audita el repo AHORA:** `git ls-files` en busca de archivos sensibles
   ya trackeados + grep de patrones (api key, token, password, Bearer).
   Reporta hallazgos antes de continuar.
3. **`docs/checklist-seguridad.md`** con los 4 principios adaptados al
   riesgo real de ESTE proyecto (¿repo público? ¿datos de clientes? ¿hay
   backend?): contexto+seguridad por adelantado · leer y entender el diff
   entero antes de aprobar · verificar antes de subir (tests + sin
   secretos) · nunca pegar claves ni datos reales en un prompt. Añade una
   tabla de amenazas reales del proyecto con su mitigación.
4. El escaneo de secretos ya quedó como paso bloqueante de `/deploy-check`.

---

## Fase 7 — Cierre y verificación del bootstrap

1. Crea `docs/README.md`: tabla que mapea cada pieza (arnés, SDD, prompts,
   ejecución, memoria, loops, seguridad) a sus artefactos, + «el flujo en
   una frase»: *leer bitácora → /nueva-feature del roadmap → implementar →
   verificar → /deploy-check → /cierre-sesion*.
2. Crea `docs/guia-prompts.md`: los 5 ejes (Rol·Contexto·Tarea·
   Restricciones·Formato) + el matiz clave: con este arnés, Contexto,
   Restricciones y Rol ya se cargan solos — el prompt diario es **Tarea
   exacta + Formato + ancla a la spec**. Incluye 3 pares malo→bueno CON
   CASOS REALES de este repo y las señales de prompt flojo («mejora X» sin
   qué ni dónde; features disfrazadas de tarea).
3. Crea `docs/guia-ejecucion.md`: cuándo Plan Mode (refactors, zonas
   críticas) vs Build (atómico) vs `/nueva-feature` (features) · cuándo
   escalar a subagentes y cuándo no (arrancan sin contexto: caros para lo
   pequeño) · higiene de contexto (Fase 5) · loop engineering: un bucle
   autónomo = acción verificable + condición de salida objetiva +
   presupuesto de iteraciones; el árbitro es la regla documentada, no el
   test.
4. Completa la sección «Documentación» del CLAUDE.md con todo lo creado.
5. Escribe la primera bitácora en `docs/sesiones/` documentando el bootstrap.
6. **Verifica el manifiesto** y muestra la tabla al usuario:

| Artefacto | Existe |
|-----------|--------|
| `CLAUDE.md` (≤500 líneas, stack real) | ☐ |
| `.mcp.json` (Context7) | ☐ |
| `.claude/skills/` (1–3, con datos reales) | ☐ |
| `.claude/commands/` (test, arregla-tests, nueva-feature, deploy-check, cierre-sesion) | ☐ |
| `.claude/agents/` (implementador `model: sonnet`, verificador sin edición) | ☐ |
| `spec/constitution/` (mission, tech-stack, roadmap) | ☐ |
| `spec/features/000-plantilla/` (spec, plan, tasks) | ☐ |
| `docs/README.md` + guías (prompts, ejecución) | ☐ |
| `docs/checklist-seguridad.md` | ☐ |
| `docs/sesiones/` (plantilla + primera bitácora) | ☐ |
| `.gitignore` verificado + auditoría de secretos hecha | ☐ |
| Los tests corren y el agente puede leer su salida | ☐ |

7. Ofrece commitear todo como «Infraestructura de agente» (separado de
   cualquier cambio de código pendiente). No hagas push sin permiso.
8. Recuerda al usuario: **reiniciar la sesión** para que carguen skills,
   comandos y agentes, y aprobar el MCP Context7 cuando lo pida.
