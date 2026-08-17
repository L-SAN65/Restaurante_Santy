# Convenciones de estilo — especificación Gherkin narrativa

Reglas extraídas de cómo se escribió `Requisitos.MD` del proyecto LUX MED. No son
sintaxis Gherkin genérica: son las decisiones de estilo concretas que hacen que ese
documento funcione como documentación *y* como base de tests de aceptación.

## Idioma

- Prosa, nombres de Feature/Scenario y contenido: **español**.
- Palabras clave de Gherkin (`Feature`, `Background`, `Scenario`, `Given`, `When`,
  `Then`, `And`): **en inglés**, sin traducir. Son las que un parser de Gherkin
  reconoce; traducirlas rompe la compatibilidad con herramientas (Cucumber,
  Behave, etc.) sin aportar nada a la legibilidad.

## Cabecera del documento

El documento abre con una nota en blockquote dirigida explícitamente "a humanos y
asistentes" que explica cómo leer las secciones que siguen — qué es invariante
inviolable, qué es comportamiento (la base de los tests), qué es contexto. Esto
importa porque un LLM u otro colaborador que entre al documento sin esta nota
puede tratar contexto legal como si fuera un requisito de software, o proponer
cambiar un invariante como si fuera negociable.

Cierra la cabecera con una línea de metadatos: `**Versión:** X · **Estado:** Y ·
**Siguiente artefacto:** Z`. Esto declara qué tan asentado está el documento sin
que haga falta leerlo entero para saberlo.

## Preámbulo — Invariantes

- Lista numerada, corta (3-8 puntos típico).
- Cada punto: **término en negrita al inicio** + explicación en una o dos frases.
- Frase explícita de que contradecirlos invalida por defecto cualquier propuesta.
- Si un invariante tiene una implicación legal/de negocio que no es comportamiento
  de software en sí (ej. "esto encadena dos titulares de datos distintos"), esa
  nota va en un blockquote aparte etiquetado `**Nota legal embebida (no es
  comportamiento):**` — nunca mezclada dentro de un Scenario.

## Terminología

- Sección de glosario **antes** de las Features, no dispersa entre ellas.
- Formato: `**Término:** definición corta.`
- Incluye aquí cualquier nombre de rama de flujo (`Rama A`, `Rama B`) o entidad
  (`PDF #1`, `PDF #2`) que los Scenarios vayan a citar por nombre repetidamente.
  Un Scenario nunca debe ser el primer lugar donde un término de dominio aparece.

## Features

- `## Feature: <nombre corto y concreto>` — nombra el *qué*, no el *cómo* técnico
  (ej. "Consulta Portal 1 (siempre) — cobertura del paciente", no "Llamada HTTP a
  endpoint de Portal 1").
- Historia de usuario clásica, indentada bajo el título:
  ```
  Como <rol>
  Quiero <objetivo>
  Para <beneficio>
  ```
  El rol puede ser humano (`Como médico`) o el propio sistema (`Como sistema`)
  cuando el comportamiento es interno y no tiene un usuario humano directo en ese
  paso — está bien usarlo así, no fuerces un actor humano donde no lo hay.
- Separa cada Feature del resto con una línea `---`.

### Background

- Úsalo dentro de una Feature cuando **todos** los Scenarios de esa Feature
  comparten el mismo `Given` de partida. Si solo lo comparten 2 de 5 Scenarios, no
  uses Background — repite el Given en esos dos.
- Un Background nunca contiene `When`/`Then`, solo `Given`.

### Scenarios

- **Título = condición + resultado, siempre específico.** Nunca genérico
  ("caso de error", "caso exitoso"). Ejemplos reales del documento:
  - "Timeout dispara reintentos acotados"
  - "Paciente no encontrado corta el flujo"
  - "PDF previo corrupto se vuelve a descargar"
  - Un título debe poder leerse solo, fuera de contexto, y seguir siendo claro.
- **Given** establece estado previo (puede ser multi-línea con `And`). **When** es
  la acción disparadora — idealmente una sola, si hay dos acciones causales
  encadenadas (ej. "se consulta Y responde no encontrado") está bien usar
  `When`/`And` para la secuencia. **Then** enumera resultados observables,
  incluyendo efectos negativos cuando importan: "y NO se consulta el Portal 2"
  es tan parte del comportamiento como lo que sí ocurre.
- **Estados y valores fijos siempre entre comillas dobles**, y con el mismo string
  literal en todo el documento: `"PENDIENTE"`, `"NO_ENCONTRADO"`,
  `"ERROR_PORTAL_1"`, `"COMPLETADO"`. Esto los convierte en un vocabulario de
  máquina de estados implícito, consistente y buscable — no cambies de
  `"NO_ENCONTRADO"` a `"NOT_FOUND"` a mitad de documento.
- **Comentarios `#`** solo para rationale que no es obvio desde el Given/When/Then
  mismo — el *por qué*, no el *qué* (que ya lo dice el Scenario). Ejemplos reales:
  - `# Sincronización con el widget legítimo del portal, no evasión del control.`
  - `# Un fallo persistente puede deberse a mantenimiento/caída del Portal 1.`
  Si el comentario solo repite lo que el Then ya dice, sóbra — bórralo.
- Evita Scenarios que mezclen dos comportamientos distintos "por si acaso" — un
  Scenario, una condición, un resultado. Si hace falta cubrir una decisión humana
  bifurcada (ej. "el médico decide continuar o pausar"), un solo Scenario con dos
  ramas de `Then` conectadas por "si X... si Y..." es aceptable cuando la decisión
  y sus dos desenlaces son inseparables en la narrativa (ver Feature de fallo
  persistente de Portal 2 en el documento de referencia).

## Apéndices

- Todo lo que no es comportamiento verificable de software va aquí, nunca en una
  Feature: stack técnico de referencia, capas legales/administrativas, puntos
  abiertos sin resolver.
- Cada Apéndice que no sea comportamiento lleva el paréntesis explícito
  `(contexto, no comportamiento)` en el título, y frecuentemente una nota al pie
  recordando que requiere validación externa (legal, de negocio) que el software
  no puede garantizar por sí solo.
- "Puntos abiertos / a confirmar" es su propio apéndice al final — un lugar único
  y visible para todo lo que quedó pendiente, en vez de TODOs sueltos dispersos
  entre Features.

## Qué NO hacer

- No mezclar una restricción legal o de negocio dentro de un `Then` como si fuera
  un requisito de software verificable por tests.
- No dejar un Scenario sin título específico.
- No introducir un segundo string para el mismo estado ya nombrado antes.
- No traducir las palabras clave de Gherkin.
- No omitir la cabecera de "cómo leer este documento" en documentos largos con
  múltiples Features — es la que evita que alguien (humano o asistente) confunda
  las tres capas (invariante / comportamiento / contexto).
