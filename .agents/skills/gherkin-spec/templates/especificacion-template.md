<!--
Plantilla de especificación de comportamiento en Gherkin, formato LUX MED.
Ver reference/convenciones.md para las reglas de estilo detalladas antes de rellenar.
Borra este bloque de comentario al usarla.
-->

# <Nombre del sistema> — Especificación de Comportamiento

> **Cómo usar este documento (para humanos y asistentes):**
> Este archivo especifica el *comportamiento observable* del sistema en Gherkin, precedido por los invariantes que NO se rediscuten y seguido por un apéndice de decisiones y pendientes.
> - El **Preámbulo** define restricciones de diseño inviolables. Cualquier propuesta que las contradiga es inválida por defecto.
> - Las **Features** describen qué hace el sistema. Son la base para tests de aceptación reales.
> - El **Apéndice** lista stack y contexto no verificable: es contexto, NO comportamiento verificable del software.
> <!-- Si aplica: añade aquí una línea que aclare cómo se relaciona lo legal/de negocio con lo que el software garantiza vs. lo que no puede garantizar por sí solo. -->
>
> **Versión:** 0.1 · **Estado:** borrador · **Siguiente artefacto:** <ej. diagrama de secuencia / wireframes / tests de aceptación>

---

## Preámbulo — Invariantes del sistema (no se rediscuten)

<!-- 3-8 puntos típico. Cada uno: **término en negrita** + 1-2 frases. No inventes
invariantes que el usuario no haya confirmado; si no hay, borra la sección. -->

1. **<Invariante 1>.** <Explicación breve.>
2. **<Invariante 2>.** <Explicación breve.>

<!-- Opcional: nota legal/de negocio embebida, NUNCA como comportamiento verificable -->
<!--
> **Nota legal embebida (no es comportamiento):** <...>
-->

---

## Terminología

<!-- Glosario de dominio citado por los Scenarios: roles, estados, ramas de flujo,
entidades. Todo estado entre comillas que aparezca en un Scenario debería poder
rastrearse aquí o a la Feature donde se define. -->

- **<Término>:** <definición corta>.
- **<Término>:** <definición corta>.

---

## Feature: <Nombre concreto del comportamiento, no técnico>

  Como <rol o "sistema">
  Quiero <objetivo>
  Para <beneficio>

  <!-- Solo si TODOS los Scenarios de esta Feature comparten el mismo Given -->
  Background:
    Given <estado de partida compartido>

  Scenario: <Condición específica → resultado específico, nunca genérico>
    Given <estado previo>
    When <acción disparadora>
    Then <resultado observable>
    And <otro resultado, incluyendo efectos negativos si importan>
    # <comentario opcional solo si aporta un "por qué" no obvio>

  Scenario: <Otro título específico>
    When <acción>
    And <acción encadenada si aplica>
    Then <resultado>

---

<!-- Repite bloques ## Feature: ... --- por cada flujo/rama principal del sistema -->

## Apéndice A — Stack de referencia (contexto, no comportamiento)

| Capa | Herramienta |
|---|---|
| <capa> | <herramienta> |

## Apéndice B — <Capas legales / administrativas / de negocio> (contexto, no comportamiento)

<!-- Solo si aplica. Deja explícito que no es comportamiento de software y qué
validación externa (legal, de negocio) requiere. -->

1. **<Punto>** — <detalle>.

> <Nota recordando que este apéndice requiere validación externa que el documento no reemplaza.>

## Apéndice C — Puntos abiertos / a confirmar

- <Pregunta o decisión pendiente 1.>
- <Pregunta o decisión pendiente 2.>
