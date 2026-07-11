# Infraestructura de trabajo con IA — mapa

**El flujo en una frase:** leer la bitácora más reciente → `/nueva-feature`
de la siguiente del roadmap → implementar → verificar → `/deploy-check` →
`/cierre-sesion`.

| Pieza | Para qué | Artefactos |
|-------|----------|------------|
| **Arnés** | Que el agente conozca las reglas sin explicárselas cada vez | `CLAUDE.md` · skills `.claude/skills/` (esquema-bd, reglas-caja, convenciones-ui) · `.mcp.json` (Context7 para docs de PySide6/pytest al día) |
| **SDD** | La spec como fuente de verdad de cada feature | `spec/constitution/` (mission, tech-stack, roadmap) · `spec/features/000-plantilla/` · comando `/nueva-feature` |
| **Prompts** | Pedir trabajo de forma que salga bien a la primera | `docs/guia-prompts.md` |
| **Ejecución** | Elegir modo de trabajo y delegación | `docs/guia-ejecucion.md` · agentes `.claude/agents/` (implementador, verificador) |
| **Memoria** | Continuidad entre sesiones | `docs/sesiones/` (bitácoras) · comando `/cierre-sesion` · higiene de contexto en `docs/guia-ejecucion.md` |
| **Loops** | Bucles autónomos con freno | `/arregla-tests` (presupuesto 5 iteraciones) · reglas de loop engineering en `docs/guia-ejecucion.md` |
| **Verificación** | Que nada se apruebe sin evidencia | `tests/` (pytest, BD temporal) · comandos `/test` y `/deploy-check` · agente `verificador` (sin permisos de edición) |
| **Seguridad** | Proteger datos reales de la tienda y el repo público | `docs/checklist-seguridad.md` · `.gitignore` · escaneo bloqueante en `/deploy-check` |

**Mentalidad:** el humano dirige, la IA ejecuta. El dueño es el responsable
final y Validador de Intentos — la potencia sin control no sirve de nada.

**Al abrir una sesión nueva:** los skills/comandos/agentes se cargan al
arrancar Claude Code; si acabas de editarlos, reinicia la sesión.
