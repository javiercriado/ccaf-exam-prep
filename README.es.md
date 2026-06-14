# Preparación CCAF — Claude Certified Architect (Foundations)

> 🇬🇧 In English? Read the **[English README](README.md)** (recommended — the exam is in English).

Un kit de estudio práctico para el examen **Claude Certified Architect – Foundations (CCAF)**,
mapeado **1:1 con la guía oficial del examen**: cada dominio, cada *task statement* y los
**6 escenarios oficiales**. Los notebooks enseñan cada concepto haciéndolo *ejecutable*:
hacen **llamadas reales a la Claude API** (algunas con el **Claude Agent SDK** y unas pocas
con la Messages API directa, solo por motivos de aprendizaje), para que veas ocurrir el
comportamiento que evalúa el examen en lugar de solo leerlo.

> [!IMPORTANT]
> **No oficial e independiente.** Este repositorio **no está afiliado a Anthropic ni
> respaldado por Anthropic.** Es un proyecto personal de estudio. Lo armé mientras me preparo
> para el examen — **todavía no he dado el examen** (preparándome, 2026). Nada aquí es un
> "volcado" de preguntas: todo se basa en la **guía oficial del examen** y en los **cursos
> oficiales de Anthropic Academy**. La guía oficial **no se redistribuye** aquí — descárgala
> de Anthropic (ver [La guía del examen](#la-guía-del-examen)).

## Por qué este repo

Hay sitios y repos de práctica que **inventan** preguntas y se alejan de lo que el examen
realmente cubre. Este es lo contrario: es deliberadamente **fiel al material oficial**. Cada
sección de notebook cita el *task statement* de la guía de forma **textual** y luego lo
convierte en código que puedes correr; cada pregunta de muestra es la oficial, mapeada al
*task statement* que evalúa. Si no está en la guía o en los cursos, no está aquí.

## Estado y validación

He **diseñado, revisado, estudiado y ejecutado personalmente cada celda** de los notebooks de
dominio que existen — es material de estudio hecho a mano, no salida de IA volcada en un repo.
El [skill `ccaf-notebook`](.claude/skills/ccaf-notebook/SKILL.md) ayuda a generar los notebooks
con un estándar de fidelidad, pero **la salida de un skill no está validada por sí sola** — el
repaso humano es lo que hace confiable una sección. Todo lo que aún no esté marcado con ✅ sigue
en revisión; verifícalo contra la guía oficial antes de confiar en ello.

**Leyenda:** ✅ validado a mano (diseñado · revisado · estudiado · ejecutado) · 🔧 en progreso ·
🧪 construido/generado, aún sin revisión manual · ⏳ no construido aún

| Notebook de dominio | Estado | | Ejercicio práctico | Estado |
|---|:--:|---|---|:--:|
| D1 · Agentic Architecture & Orchestration | ✅ | | 01 · support-agent | 🧪 |
| D2 · Tool Design & MCP Integration | ✅ | | 02 · claude-code-team | 🧪 |
| D5 · Context Management & Reliability | 🔧 | | 03 · extraction-pipeline | 🧪 |
| D3 · Claude Code Configuration & Workflows | ⏳ | | 04 · multi-agent-research | 🧪 |
| D4 · Prompt Engineering & Structured Output | ⏳ | | 05 · cicd-review | 🧪 |

(Los ejercicios hoy corren y son portables, pero aún no les hago mi pase de revisión/ajuste
manual — es el siguiente paso después de D5.)

## Empieza aquí — prerrequisitos (hazlos primero)

Este kit asume que ya hiciste los **cuatro cursos oficiales de Anthropic Academy**. Hazlos
primero, **toma notas a mano** y **completa sus ejercicios** — ahí se construye la memoria
muscular. Su código está en [`claude-with-anthropic-api/`](claude-with-anthropic-api/).

| Curso oficial | Mapea principalmente a |
|---|---|
| Building with the Claude API | **D4** Prompt Engineering & Structured Output |
| Claude Code in Action | **D3** Claude Code Configuration & Workflows |
| Introduction to Model Context Protocol (MCP) | **D2** Tool Design & MCP Integration |
| Introduction to Agent Skills | **D3** Claude Code Configuration & Workflows |

Los cursos están en **[Anthropic Academy](https://anthropic.skilljar.com/)** (y replicados en
[github.com/anthropics/courses](https://github.com/anthropics/courses)). Todo — los cursos y
el examen — es **en inglés**, por eso este kit está en inglés (este README en español es solo
una ayuda).

## El examen de un vistazo

- **60 preguntas**, **120 minutos**, opción múltiple (1 correcta + 3 distractores).
- Se eligen **4 de 6 escenarios** al azar en tu rendición.
- Aprobar = **720 / 1000** escalado. **Sin penalización por adivinar → nunca dejes una en blanco.**
- Pesos por dominio: **D1 27% · D3 20% · D4 20% · D2 18% · D5 15%**.

## Qué contiene

```
ccaf-prep/
  notebooks/      un notebook por dominio + el examen de práctica
    D1_agentic_loops.ipynb          ✅  D1 · Agentic Architecture & Orchestration (27%)
    D2_tool_design_mcp.ipynb        ✅  D2 · Tool Design & MCP Integration (18%)
    D5_context_reliability.ipynb    🔧  D5 · Context Management & Reliability (15%)
    D3_*.ipynb                      ⏳  D3 · Claude Code Configuration & Workflows (20%)
    D4_*.ipynb                      ⏳  D4 · Prompt Engineering & Structured Output (20%)
    mock_exam_and_review.ipynb      checklist de cobertura + las 12 preguntas por escenario
    README.md                       la guía de orden de estudio
  exercises/      cinco prácticas ejecutables, cada una multi-dominio
    01-support-agent/      02-claude-code-team/      03-extraction-pipeline/
    04-multi-agent-research/         05-cicd-review/
  MAPPING.md      task statement abstracto → archivo:línea concreto → pregunta (el índice)
  STUDY_PLAN.md   el cronograma completo y la justificación
  reference/      donde TÚ pones tu exam_guide.txt descargado (git-ignored — ver su README)
claude-with-anthropic-api/   el código y ejercicios de los cursos oficiales de Anthropic
.claude/skills/ccaf-notebook/   el skill usado para generar los notebooks (ver abajo)
```

Cada notebook de dominio sigue la misma anatomía por *task statement*: **cita textual de la
guía → tabla en lenguaje claro → una celda ejecutable que lo hace observable → los
anti-patrones como código (las respuestas incorrectas del examen) → un puntero a la línea
equivalente en tu propio código de curso/ejercicio → un auto-test**. Cada uno termina con las
**preguntas de muestra oficiales** de ese dominio (respuestas ocultas).

## Cómo estudiar (orden recomendado)

El orden es **guiado por dependencias**, para que cada ejercicio se desbloquee apenas se
cubren sus dominios — no por peso del examen:

1. **Notebooks:** `D1 → D2 → D5 → D3 → D4`. Corre todas las celdas; haz las preguntas de
   muestra de forma activa (tapa la respuesta, justifica por qué cada distractor está mal,
   luego revela).
2. **Ejercicios, en olas** (son multi-dominio — ninguno es de un solo dominio):

   | Después de estudiar… | Haz ejercicios | Dominios que usa |
   |---|---|---|
   | D1 + D2 + D5 | **Ej1** y luego **Ej4** | D1 + D2 + D5 |
   | + D3 | **Ej2** | D3 + D2 |
   | + D4 | **Ej3** ∥ **Ej5** | D4 + D5 / D3 + D4 |

3. **Consolida** en [`mock_exam_and_review.ipynb`](ccaf-prep/notebooks/mock_exam_and_review.ipynb):
   marca la cobertura conforme terminas cada dominio, y al final haz el simulacro agrupado
   por escenario.
4. **Por último**, rinde el **Examen de Práctica** oficial (Skilljar) con tiempo cronometrado.

Mantén [`ccaf-prep/MAPPING.md`](ccaf-prep/MAPPING.md) abierto como índice. La justificación
completa está en [`ccaf-prep/STUDY_PLAN.md`](ccaf-prep/STUDY_PLAN.md).

## Configuración

Necesitas **Python 3.12+** y **[uv](https://docs.astral.sh/uv/)**.

```bash
# 1. instala dependencias (crea ccaf-prep/.venv)
cd ccaf-prep && uv sync

# 2. agrega tu API key — copia la plantilla en la raíz del repo y edítala
cp ../.env.example ../.env
#    luego pon tu key en ../.env:  ANTHROPIC_API_KEY=sk-ant-...
```

El `.env` se descubre automáticamente desde cualquier carpeta del repo (no configuras rutas).
Las llamadas **usan `claude-haiku-4-5` por defecto** — el modelo más barato — porque estas
demos enseñan el *mecanismo*, no la "inteligencia" del modelo. Cámbialo en todos lados con
`CLAUDE_MODEL=...` en `.env`.

**Correr un notebook:** ábrelo en VS Code / Jupyter y elige el kernel `ccaf-prep`, o corre
todas las celdas sin interfaz. **Correr un ejercicio:**

```bash
cd ccaf-prep/exercises/01-support-agent && uv run python agent.py
```

Cada carpeta de ejercicio tiene su propio `README.md` con los pasos, las etiquetas de
*task statement* y los **toggles de anti-patrón** para probar (cambia un flag y observa cómo
falla el enfoque incorrecto).

### Mantén tus outputs locales, sin commitearlos

Los outputs de los notebooks se quitan automáticamente al commitear (diffs limpios, sin
filtrar respuestas del API) pero se quedan en tu copia local. Actívalo una vez por clon:

```bash
cd ccaf-prep && uv run nbstripout --install --attributes ../.gitattributes
```

### Lleva tu propio progreso

El examen de práctica tiene un checklist de cobertura. Para registrar tu progreso **sin
commitearlo**, haz una copia personal (está git-ignored):

```bash
cd ccaf-prep/notebooks && cp mock_exam_and_review.ipynb mock_exam_and_review.personal.ipynb
```

Guarda los escaneos de tus notas a mano o cualquier nota privada en una carpeta `personal/`
(git-ignored).

## La guía del examen

La guía oficial **no se incluye** (es material de Anthropic). Descarga la **Claude Certified
Architect – Foundations Certification Exam Guide** desde Anthropic. Si quieres que el skill
generador regenere dominios, guarda el texto de la guía como
`ccaf-prep/reference/exam_guide.txt` (git-ignored) — las **12 preguntas de muestra**
reproducidas en los notebooks son las que Anthropic publica como muestra en esa guía.

## Cómo se construyeron los notebooks

Los notebooks se generaron y mantienen con un skill de Claude Code,
[`.claude/skills/ccaf-notebook/`](.claude/skills/ccaf-notebook/SKILL.md), que impone las
reglas de fidelidad de arriba (citas textuales, llamadas reales al API, punteros
`archivo:línea` verificados). Se incluye como referencia por si quieres extender o regenerar
dominios.

## Sobre mí

**Javier Criado Gómez** — AI Engineer.
LinkedIn: https://www.linkedin.com/in/javierjcriadogomez/ · preguntas, sugerencias y correcciones son
bienvenidas (abre un issue o un PR). Comparto esto para ayudar a otros a certificarse mientras
yo mismo me preparo; cuando rinda el examen actualizaré esta nota.

## Contribuir

¿Encontraste algo que se aleja del material oficial, o una celda que no corre? Abre un issue
o un PR. El criterio es **fidelidad a la guía y los cursos oficiales** — las correcciones que
lo acercan a la fuente son las más valiosas.

## Aviso

Material de estudio comunitario e independiente. **No afiliado a Anthropic ni respaldado por
Anthropic.** "Claude" y "Anthropic" son marcas de Anthropic. La guía oficial y los cursos son
de Anthropic; aquí se referencian y enlazan, no se redistribuyen. Se ofrece tal cual, con
fines educativos.
