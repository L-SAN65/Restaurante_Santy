# gherkin-spec

Skill de [Claude Code](https://claude.com/claude-code) para generar y mantener
especificaciones de comportamiento en **Gherkin**, usando un formato narrativo
que va más allá del bloque `Feature/Scenario` suelto: separa explícitamente
**invariantes**, **comportamiento verificable** y **contexto** (stack técnico,
capas legales, pendientes), de modo que el documento resultante sirva como
fuente de verdad tanto para diseño como para tests de aceptación.

## Por qué

Es habitual que un documento de requisitos mezcle, sin darse cuenta, tres
cosas de naturaleza muy distinta:

1. **Invariantes** — reglas de arquitectura o negocio que no se rediscuten.
2. **Comportamiento** — lo que sí se modela en Gherkin, es negociable y
   evoluciona con el sistema.
3. **Contexto** — stack técnico, capas legales/administrativas, decisiones
   pendientes. No es comportamiento verificable y no debería vivir dentro de
   un `Scenario`.

Esta skill fuerza esa separación en cada documento que genera, para que ni un
humano ni otro asistente confundan una nota legal con un requisito de
software, o un invariante con algo negociable.

## Estructura del repositorio

```
gherkin-spec/
├── SKILL.md                          # Definición de la skill: cuándo usarla y workflow
├── reference/
│   └── convenciones.md               # Reglas de estilo detalladas (títulos, Background,
│                                      # comentarios, estados entre comillas, tono)
└── templates/
    └── especificacion-template.md    # Esqueleto listo para copiar y rellenar
```

## Instalación

Copia esta carpeta dentro de tu directorio de skills de Claude Code, por
ejemplo:

```bash
git clone https://github.com/ElMichi08/gherkin-spec.git ~/.claude/skills/gherkin-spec
```

Claude Code detecta automáticamente la skill a partir del frontmatter de
`SKILL.md`.

## Uso

Invócala cuando necesites documentar/especificar el comportamiento de un
sistema antes de escribir código, por ejemplo:

- "Escribe el Requisitos.MD de este módulo en Gherkin."
- "Especifica el comportamiento de este flujo antes de implementarlo."
- "Extiende el documento de requisitos que ya tenemos con un nuevo feature."

La skill:

1. Recolecta invariantes, terminología y flujos principales antes de escribir
   (o pregunta si falta información — no inventa invariantes).
2. Estructura el documento siguiendo `templates/especificacion-template.md`.
3. Aplica las reglas de estilo de `reference/convenciones.md`.
4. Revisa el resultado contra un checklist antes de darlo por terminado.

Cada `Feature` se redacta como historia de usuario clásica (`Como / Quiero /
Para`) y cada `Scenario` lleva un título específico (condición → resultado),
nunca genérico. Las palabras clave de Gherkin (`Feature`, `Given`, `When`,
`Then`...) se mantienen en inglés por compatibilidad con herramientas como
Cucumber o Behave; el resto del contenido va en español.

## Licencia

[MIT](LICENSE)
