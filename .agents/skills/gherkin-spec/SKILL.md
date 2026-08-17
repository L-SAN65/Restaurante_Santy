---
name: gherkin-spec
description: Genera y mantiene especificaciones de comportamiento en Gherkin con el formato narrativo usado en el proyecto LUX MED — Preámbulo de invariantes, Terminología, Features/Scenarios en español, y Apéndices que separan stack técnico y contexto legal del comportamiento verificable. Usar cuando el usuario pida escribir/documentar requisitos, redactar un Requisitos.MD, especificar el comportamiento de un sistema en Gherkin, o iniciar la fase de diseño de un proyecto nuevo antes de escribir código.
---

# Especificación de comportamiento en Gherkin (formato LUX MED)

Genera documentos de requisitos que usan Gherkin como *columna vertebral*, pero el
documento completo es más que Gherkin: separa explícitamente tres cosas que casi
siempre se mezclan por descuido —

1. **Invariantes** (reglas que no se discuten, van antes de cualquier feature).
2. **Comportamiento** (lo que sí se modela en Gherkin, es negociable, evoluciona).
3. **Contexto** (stack técnico, capas legales, pendientes — no es comportamiento
   verificable y debe quedar marcado como tal para que nadie lo confunda con un
   requisito de software).

Esta separación es la razón de ser del formato. No generes "solo el bloque Gherkin"
sin las secciones que lo envuelven — sin ellas el documento pierde el propósito de
servir como fuente de verdad para diseño + tests de aceptación.

## Cuándo usar esta skill

- El usuario pide documentar/especificar requisitos de un sistema o feature nueva.
- El usuario pide "escribir esto en Gherkin" o "un Requisitos.MD".
- Se está en fase de diseño (pre-código) y hace falta fijar comportamiento antes de
  implementar.
- Se pide actualizar/extender un documento de requisitos ya escrito con este formato.

## Workflow

### 1. Recolecta antes de escribir

No generes el documento a partir de suposiciones. Si el usuario no lo ha dado ya en
la conversación, pregunta (o infierelo del código/contexto existente y confírmalo):

- **Nombre del sistema** y una frase de qué hace.
- **Invariantes**: restricciones de arquitectura o negocio que NO se van a
  rediscutir (ej: on-premise, sin LLM, sin manejo de credenciales, retención de
  datos). Suelen ser 3-8 puntos. Si el usuario no tiene invariantes claros todavía,
  es una señal legítima de que el documento debe omitir esa sección por ahora, no
  de que debas inventarlos.
- **Terminología**: términos de dominio que se van a repetir en los Scenarios
  (roles, estados, ramas de flujo, entidades). Si un Scenario va a usar un estado
  entre comillas como `"COMPLETADO"`, ese estado debe poder rastrearse a esta
  sección o a un Feature que lo defina.
- **Flujos/ramas principales** del sistema, a alto nivel, para agrupar en Features.
- **Qué es contexto y no comportamiento**: stack técnico previsto, capas legales o
  administrativas, decisiones pendientes de confirmar.

### 2. Estructura el documento

Sigue el esqueleto de `templates/especificacion-template.md` en orden. Antes de
escribir Features, lee `reference/convenciones.md` — contiene las reglas de estilo
concretas (cómo titular un Scenario, cuándo usar `Background`, cuándo un comentario
`#` aporta y cuándo sobra, cómo marcar estados). Son las reglas que hacen que el
documento sea reutilizable como base de tests de aceptación, no prosa suelta con
palabras clave de Gherkin encima.

### 3. Revisa contra el checklist antes de entregar

Antes de considerar el documento terminado, verifica:

- [ ] La nota de cabecera dice explícitamente cómo leer el documento (qué es
      invariante, qué es comportamiento, qué es contexto).
- [ ] Ningún invariante del Preámbulo se repite o se contradice en un Scenario.
- [ ] Todo estado/valor fijo citado en un Scenario (`"NO_ENCONTRADO"`, etc.) es
      consistente en TODO el documento — mismo string, siempre entre comillas.
- [ ] Cada Scenario tiene un título específico (condición → resultado), no genérico.
- [ ] Lo legal/administrativo/de stack vive en Apéndices, marcado explícitamente
      como "no es comportamiento".
- [ ] Si algo quedó sin resolver, está en un Apéndice de "Puntos abiertos", no
      enterrado como un TODO suelto dentro de un Scenario.
- [ ] El documento declara versión/estado/siguiente artefacto en la cabecera.

### 4. Mantenimiento de documentos existentes

Si se pide extender un `Requisitos.MD` ya escrito con este formato: lee el
documento completo primero, detecta su Terminología y convenciones de nombres de
estado ya en uso, y reutilízalas — no introduzcas un vocabulario paralelo para el
mismo concepto (ej. no mezcles `"NO_ENCONTRADO"` con `"NOT_FOUND"` en el mismo
documento).

## Archivos de esta skill

- `reference/convenciones.md` — reglas de estilo detalladas (títulos de Scenario,
  Background, comentarios, estados entre comillas, tono).
- `templates/especificacion-template.md` — esqueleto completo listo para copiar y
  rellenar, con las secciones en el orden correcto y comentarios `<!-- -->`
  indicando qué va en cada una.
