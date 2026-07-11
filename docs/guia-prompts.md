# Guía de prompts — cómo pedir trabajo en este proyecto

## Los 5 ejes de un buen prompt

**Rol · Contexto · Tarea · Restricciones · Formato.**

El matiz clave de ESTE repo: con el arnés montado, **Rol, Contexto y
Restricciones ya se cargan solos** (CLAUDE.md, skills, spec). El prompt del
día a día se reduce a:

> **Tarea exacta + Formato de salida + ancla a la spec.**

No repitas lo que el arnés ya sabe ("es un POS en Python con PySide6…");
di exactamente qué quieres, dónde, y contra qué spec/criterio se mide.

## Pares malo → bueno (casos reales de este repo)

### 1. Cambio acotado

- ❌ *«Mejora el corte de caja»*
  (¿mejorar qué? ¿la fórmula, el diálogo, el reporte? La fórmula es zona
  delicada y ni siquiera sabes si la va a tocar.)
- ✅ *«En `DialogoCierreCaja`, agrega un renglón que muestre el total de
  ventas con Tarjeta + Transferencia juntas, etiquetado "No efectivo".
  NO toques la fórmula de `esperado` en `resumen_caja_sesion`. Formato:
  diff propuesto + captura del diálogo corriendo.»*

### 2. Bug

- ❌ *«El inventario está mal»*
- ✅ *«Al registrar una compra a proveedor, el stock del producto sube
  pero no aparece fila en `movimientos_inventario` (invariante de
  CLAUDE.md). Reproduce con una BD temporal, encuentra la causa raíz en
  el flujo de compras y propón el fix. Formato: diagnóstico con
  archivo:línea ANTES de tocar código.»*

### 3. Feature disfrazada de tarea (la trampa más común)

- ❌ *«Agrega que se pueda vender jamón por kilo»*
  (parece una tarea; en realidad cambia esquema de BD, ticket, corte y
  reportes → es la feature #3 del roadmap.)
- ✅ *«Corre `/nueva-feature productos-a-granel`. En la spec, parte de:
  se vende por peso (kg/gr) huevo, jamón y queso; el vendedor captura
  peso O monto; el stock pasa a decimales.»*

## Señales de prompt flojo (si detectas una, reescribe)

- «Mejora / arregla / optimiza X» **sin qué ni dónde**.
- Pedir código sin decir **cómo se verá verificado** (test, captura, corte
  que cuadra).
- Una "tarea" que toca BD + dinero + UI a la vez → es una **feature**:
  `/nueva-feature`.
- Pegar datos reales de la tienda en el prompt (prohibido: checklist de
  seguridad).
- Pedir "hazlo como creas mejor" en zona de dinero — ahí las decisiones
  las toma el dueño con una spec.
