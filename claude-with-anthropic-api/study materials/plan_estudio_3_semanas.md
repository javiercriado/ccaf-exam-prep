# Plan de Estudio Intensivo — Claude Certified Architect: Foundations
### 3 Semanas · Cobertura completa de los 5 dominios del examen

---

## Distribución de dominios

| Dominio | Peso | Semana principal |
|---|---|---|
| 1. Arquitectura de agentes y orquestación | 27% | Semana 2 |
| 2. Diseño de herramientas e integración MCP | 18% | Semana 2 |
| 3. Configuración y flujos de trabajo de Claude Code | 20% | Semana 3 |
| 4. Ingeniería de prompts y salida estructurada | 20% | Semana 1–2 |
| 5. Gestión de contexto y confiabilidad | 15% | Semana 3 |

---

## SEMANA 1 — Fundamentos y API

### Día 1 — Conceptos base del modelo y la API

- Qué es Claude y la familia de modelos (Opus, Sonnet, Haiku)
- Diferencia entre LLM, agente y sistema multiagente
- Principio de statelessness: el modelo no guarda estado entre llamadas
- Estructura de una solicitud a la Messages API: `model`, `max_tokens`, `system`, `messages`, `tools`, `tool_choice`
- Roles de mensajes: `user`, `assistant`, `tool_result`
- Obligatoriedad de enviar el historial completo en cada llamada
- El campo `stop_reason`: `end_turn`, `tool_use`, `max_tokens`, `stop_sequence`
- Cuándo actuar ante cada valor de `stop_reason`

### Día 2 — System prompt y ventana de contexto

- Qué es el system prompt y cómo se diferencia del array `messages`
- Prioridad del system prompt sobre los mensajes del usuario
- Efectos secundarios no deseados de instrucciones en el system prompt (asociaciones involuntarias con herramientas)
- Qué compone la ventana de contexto: system prompt + historial + definiciones de herramientas + resultados de herramientas
- El efecto "lost-in-the-middle": qué es, por qué ocurre, cómo mitigarlo
- Acumulación de resultados de herramientas y desperdicio de contexto
- Pérdida de valores numéricos y fechas durante sumarización progresiva

### Día 3 — Tool use: fundamentos

- Qué es `tool_use`: el modelo genera la solicitud, tu código la ejecuta
- Estructura de definición de una herramienta: `name`, `description`, `input_schema`
- Por qué la descripción es el mecanismo principal de selección de herramientas
- Qué incluir en una descripción: qué hace, qué devuelve, formatos de entrada, casos límite, cuándo usar vs alternativas
- El parámetro `tool_choice`: `auto`, `any`, `tool` (forzado)
- Cuándo usar cada modo de `tool_choice`
- Diferencia entre errores sintácticos y semánticos en salida estructurada
- `tool_use` con JSON schema: garantiza sintaxis, no semántica

### Día 4 — Diseño de esquemas JSON

- Campos `required` vs opcionales: cuándo marcar cada uno
- Campos nullables: `"type": ["string", "null"]` para evitar alucinaciones
- Uso de `enum` para mapear lenguaje natural a valores de backend
- Agregar `"other"` + campo de detalle en enums para no perder datos
- Agregar `"unclear"` en enums para honestidad sobre incertidumbre
- Diseño de esquemas para capturar valores en conflicto con provenance (fuente + valor)
- Patrón `stated_total` + `calculated_total` + `conflict_detected` para auto-corrección
- Validación con Pydantic: validación estructural vs semántica
- Generación de JSON Schema desde modelos Pydantic

### Día 5 — Ingeniería de prompts: técnicas core

- Few-shot prompting: qué es, por qué supera a las instrucciones de texto
- Tipos de ejemplos few-shot: escenarios ambiguos, formato de salida, código aceptable vs problemático, extracción de distintos formatos de documento, medidas informales
- Criterios explícitos vs instrucciones vagas: cómo definir condiciones de flagging precisas
- Definición de criterios de severidad con ejemplos concretos (CRITICAL, HIGH, MEDIUM, LOW)
- Reglas de normalización en prompts: fechas ISO 8601, moneda, porcentajes
- El patrón "entrevista": cuándo Claude debe hacer preguntas antes de implementar
- Validación y retry-with-feedback: cuándo funciona y cuándo no
- Ciclo validar → construir mensaje de error → reenviar con contexto

### Día 6 — Prompt chaining y descomposición de tareas

- Prompt chaining: dividir tareas complejas en pasos secuenciales enfocados
- Por qué el chaining evita la dilución de atención
- Pipelines fijos vs descomposición adaptativa dinámica: cuándo usar cada uno
- Revisión de código multi-pasada: pasada por archivo + pasada de integración
- Por qué una sola pasada sobre 14 archivos es un antipatrón
- Cuándo usar prompt chaining vs agentes dinámicos

### Día 7 — Repaso Semana 1 + práctica de preguntas

- Repaso de todos los conceptos de la semana
- Práctica con preguntas tipo examen de los temas cubiertos
- Revisión de antipatrones identificados hasta ahora

---

## SEMANA 2 — Arquitectura de Agentes, MCP y Herramientas

### Día 8 — El ciclo de agente (Agentic Loop)

- Qué es el agentic loop: secuencia de acciones autónomas
- Flujo completo: enviar solicitud → recibir respuesta → verificar `stop_reason` → ejecutar herramienta → agregar resultado → repetir
- Enfoque model-driven vs árboles de decisión predefinidos
- Antipatrones del agentic loop: parsear texto para detectar finalización, límite arbitrario de iteraciones, verificar contenido de texto como señal de fin
- La única señal confiable de finalización: `stop_reason == "end_turn"`
- `AgentDefinition`: parámetros `name`, `description`, `system_prompt`, `allowed_tools`
- Principio de privilegios mínimos en `allowed_tools`

### Día 9 — Arquitectura hub-and-spoke y subagentes

- Topología hub-and-spoke: coordinador + subagentes especializados
- Responsabilidades del coordinador: descomposición, delegación, agregación, manejo de errores, comunicación
- Principio crítico: los subagentes tienen contexto aislado
- Los subagentes NO heredan el historial del coordinador
- Obligatoriedad de pasar contexto explícitamente en el prompt del subagente
- Antipatrón: `Task: "Analiza el documento"` sin contexto
- Patrón correcto: incluir documento completo + resultados previos + formato de salida
- La herramienta `Task` para generar subagentes
- Paralelismo: el coordinador puede llamar múltiples `Task` en una respuesta
- Toda comunicación fluye por el coordinador (observabilidad y control de errores)

### Día 10 — Hooks en el Agent SDK

- Qué son los hooks: interceptación y transformación en puntos del ciclo de vida
- `PostToolUse`: intercepta resultado de herramienta antes de pasarlo al modelo
- `PreToolUse`: bloquea acciones que violan política antes de ejecutarlas
- Caso de uso: normalizar formatos de fecha de distintos servidores MCP
- Caso de uso: bloquear reembolsos por encima de umbral
- Hooks vs instrucciones en prompts: determinístico vs probabilístico
- Cuándo usar hooks: reglas de negocio críticas, operaciones financieras, cumplimiento
- Cuándo usar prompts: preferencias generales, recomendaciones, formato
- Regla: si el fallo tiene consecuencias financieras, legales o de seguridad → hook

### Día 11 — Model Context Protocol (MCP): fundamentos

- Qué es MCP: protocolo abierto para conectar sistemas externos a Claude
- Los tres tipos de recursos MCP: Tools, Resources, Prompts
- Servidores MCP: proceso que implementa el protocolo y expone herramientas/recursos
- Descubrimiento automático de herramientas al conectar un servidor
- Configuración de proyecto `.mcp.json`: para uso en equipo, gestionado en VCS
- Configuración de usuario `~/.claude.json`: personal, no compartida por VCS
- Variables de entorno para secretos: `${GITHUB_TOKEN}` en lugar de tokens directos
- Cuándo usar servidores MCP comunitarios vs construir propios
- La bandera `isError: true` en respuestas MCP
- Error estructurado vs error genérico: qué información debe incluir un error útil
- Recursos MCP: datos de contexto sin ejecutar acciones (catálogos, esquemas, documentación)
- Ventaja de los recursos: el agente obtiene un "mapa" sin llamadas exploratorias

### Día 12 — Diseño avanzado de herramientas

- Descripciones de herramientas: el mecanismo principal de selección
- Cómo evitar confusión entre herramientas similares: definir límites negativos explícitos
- Ejemplo: `delete_file` vs `archive_file`: incluir "NO usar para archivos de backup"
- Preferencia de herramientas integradas sobre MCP: cómo contrarrestarla con descripciones
- Diseño de parámetros con `enum` para mapear lenguaje natural a valores de backend
- Paginación en herramientas: primera página + metadata (`total_matches`, `next_cursor`)
- Por qué truncar silenciosamente resultados es un antipatrón
- Internalizar dependencias predecibles: `get_neighborhood_info(property_id)` en lugar de dos pasos
- Normalización de respuestas heterogéneas: esquema común antes de devolver al agente
- Patrón lookup + action: `search_games` → `game_id` → `update_score(game_id)`
- Reglas de negocio en la lógica de la herramienta, no en el prompt
- Manejo de errores en herramientas: retry interno para transitorios, retorno inmediato para sintácticos
- Scoping dinámico de herramientas: `search_connectors` para reducir de 50+ a 2-3 herramientas relevantes

### Día 13 — Seguridad, confianza y MCP annotations

- Anotaciones MCP: `readOnlyHint`, `destructiveHint` como metadata auto-reportada
- Por qué las anotaciones MCP son metadata no confiable
- Política de bypass de confirmación basada en confianza del vendor, no en las etiquetas
- Prompt injection: qué es, cómo los agentes son vulnerables
- Principio de mínimo privilegio en herramientas y agentes
- Validación de entradas en herramientas como barrera de seguridad
- Enforcement de reglas de negocio en backend (determinístico) vs prompts (probabilístico)

### Día 14 — Repaso Semana 2 + práctica de preguntas

- Repaso de arquitectura de agentes, MCP y diseño de herramientas
- Práctica con preguntas tipo examen de los temas cubiertos
- Revisión de antipatrones de la semana

---

## SEMANA 3 — Claude Code, Contexto, Confiabilidad y Batch API

### Día 15 — Claude Code: CLAUDE.md y configuración

- Qué es Claude Code y para qué se usa
- Jerarquía de CLAUDE.md: usuario (`~/.claude/CLAUDE.md`), proyecto (`.claude/CLAUDE.md`), directorio
- Qué va en cada nivel: personal vs equipo vs directorio específico
- Error típico: instrucciones de proyecto en nivel de usuario → nuevo miembro no las recibe
- Sintaxis `@path` para importar archivos externos en CLAUDE.md
- Reglas de `@path`: sin espacio, rutas relativas o absolutas, profundidad máxima 5 niveles
- El directorio `.claude/rules/`: alternativa modular a CLAUDE.md monolítico
- Frontmatter YAML con campo `paths` para carga condicional de reglas
- Cuándo usar `.claude/rules/` con `paths` vs CLAUDE.md a nivel de directorio

### Día 16 — Claude Code: Skills, comandos slash y sesiones

- Comandos slash: plantillas de prompts reutilizables invocadas con `/nombre`
- Formato `.claude/commands/` (heredado, compatible) vs `.claude/skills/` (actual)
- Comandos de proyecto (en VCS, disponibles para el equipo) vs comandos de usuario (personales)
- Skills: comandos avanzados con frontmatter SKILL.md
- Parámetros de frontmatter: `context: fork`, `allowed-tools`, `argument-hint`
- `context: fork`: ejecuta la skill en subagente aislado, no contamina la sesión principal
- Cuándo usar una skill vs CLAUDE.md
- El comando `/compact`: compresión de contexto, riesgo de pérdida de valores exactos
- El comando `/memory`: gestión de memoria entre sesiones, edita CLAUDE.md
- `--resume <session-name>`: retomar sesión nombrada con contexto guardado
- `fork_session`: rama independiente desde contexto compartido para comparar enfoques
- Cuándo iniciar sesión nueva vs reanudar

### Día 17 — Claude Code: modo de planificación y CI/CD

- Planning mode vs ejecución directa: cuándo usar cada uno
- Planning mode: solo investiga y planifica, sin cambios, usa Read/Grep/Glob
- Cuándo usar planning mode: cambios a gran escala, múltiples enfoques, base de código desconocida, migraciones de 45+ archivos
- Cuándo usar ejecución directa: correcciones de archivo único, cambios bien comprendidos
- Enfoque combinado: planning → aprobación → ejecución
- Subagente Explore: aísla salida verbosa, devuelve solo resumen
- La bandera `-p` / `--print`: modo no interactivo para CI/CD
- `--output-format json` + `--json-schema` para salida estructurada en pipelines
- Aislamiento de contexto de sesión para revisión de código: instancia independiente
- Prevención de comentarios duplicados en re-revisiones: incluir resultados previos en contexto
- Integración con GitHub Actions y GitLab CI/CD
- Headless mode: ejecución no interactiva en automatización

### Día 18 — Gestión de contexto avanzada

- Degradación de contexto en sesiones largas: respuestas inconsistentes, referencias a "patrones típicos"
- Scratchpad files: persistir hallazgos clave entre límites de contexto
- Delegación a subagentes para aislar salida verbosa de exploración
- Persistencia de estado estructurada para recuperación ante fallos: manifests
- Diseño de crash recovery: cada agente exporta estado a ubicación conocida, coordinador carga manifest al reanudar
- Inyección de resúmenes de fase anterior en el contexto inicial de la siguiente fase
- Uso de `/compact` en sesiones de exploración extendidas
- Estrategias de memoria: cuándo usar CLAUDE.md, scratchpad, resúmenes explícitos

### Día 19 — Confiabilidad, escalada y human-in-the-loop

- Cuándo escalar a un humano: solicitud explícita de gerente, política no cubre el caso, sin progreso, umbral financiero, múltiples coincidencias en búsqueda
- Qué NO es un desencadenante confiable: análisis de sentimiento, autoevaluación de confianza del modelo, clasificador automático
- Patrones de escalada: inmediata, con intento de solución, matizada (reconocer → resolver → escalar en reiteración)
- Escalada por brecha en política: cuando la política no cubre el caso específico
- Protocolo estructurado de traspaso: qué debe incluir el resumen para el operador humano
- Confianza del modelo: el modelo puede estar equivocado con alta confianza
- Field-level confidence scores: calibración con validation sets etiquetados
- Stratified random sampling: auditar muestras de extracciones de alta confianza
- Análisis de precisión por tipo de documento y por campo, no solo en agregado
- Routing de revisión humana: baja confianza o fuentes ambiguas/contradictorias

### Día 20 — Manejo de errores en sistemas multiagente

- Categorías de errores: transitorios, de validación, de negocio, de permisos
- Errores transitorios: retry con backoff exponencial
- Errores de validación: modificar solicitud y reintentar
- Errores de negocio: explicar al usuario, proponer alternativa
- Errores de permisos: escalar
- Antipatrones de manejo de errores: status genérico, supresión silenciosa, abortar workflow completo, retries infinitos en subagente
- Error estructurado: incluir tipo de fallo, query intentada, resultados parciales, alternativas
- Distinción entre fallo de acceso (timeout) y resultado vacío válido (sin coincidencias)
- Recuperación local en subagentes: 1-2 retries, luego propagar al coordinador
- Propagación de errores: qué información debe incluir el error para que el coordinador pueda recuperarse
- Síntesis con anotaciones de cobertura: indicar qué hallazgos tienen soporte vs qué áreas tienen gaps

### Día 21 — Batch API, SLA y procesamiento masivo

- Message Batches API: ahorro del 50%, ventana de hasta 24 horas, sin garantía de latencia
- Multi-turn tool calling: NO soportado en Batch API
- El campo `custom_id`: vincular solicitud con respuesta, reenviar solo los fallidos
- Cuándo usar Batch API vs API sincrónica: criterios de decisión
- Casos de uso de Batch: reportes nocturnos, auditorías semanales, procesamiento masivo de documentos
- Casos de uso de API sincrónica: verificación pre-merge, revisión interactiva, respuesta inmediata requerida
- Cálculo de SLA: ventana de envío = SLA total − 24 horas de procesamiento
- Ejemplo: SLA de 30 horas → enviar cada 4 horas (4h espera + 24h procesamiento = 28h, buffer de 2h)
- Por qué enviar cada 6 horas falla: 6 + 24 = 30h exacto, sin buffer
- Estrategia de refinamiento antes de batch masivo: refinar prompt en muestra representativa primero
- Manejo de fallos parciales: identificar por `custom_id`, modificar estrategia, reenviar solo fallidos
- Dividir documentos largos que exceden context limit

### Día 22 — Provenance, síntesis multiagente y extracción estructurada

- Preservación de provenance en síntesis: cómo se pierde la atribución de fuentes durante sumarización
- Structured claim-source mappings: URL de fuente, nombre de documento, extracto relevante
- Cómo los agentes downstream deben preservar y fusionar mappings de fuentes
- Manejo de estadísticas en conflicto de fuentes creíbles: anotar conflictos con atribución, no seleccionar arbitrariamente
- Datos temporales: incluir fechas de publicación/recolección para evitar malinterpretación de diferencias temporales
- Secciones de síntesis: hallazgos bien establecidos vs hallazgos en disputa
- Renderizado apropiado por tipo de contenido: datos financieros como tablas, noticias como prosa, hallazgos técnicos como listas estructuradas
- Extracción de documentos con valores en conflicto: capturar todos los valores con ubicación de fuente
- Antipatrón: colapsar prematuramente a un solo valor cuando hay conflicto

### Día 23 — Escenarios del examen: repaso integrado

- Escenario 1: Agente de soporte al cliente — herramientas MCP, escalada, hooks, resolución en primer contacto
- Escenario 2: Generación de código con Claude Code — CLAUDE.md, skills, planning mode
- Escenario 3: Sistema de investigación multiagente — coordinador, subagentes paralelos, síntesis con provenance
- Escenario 4: Herramientas de productividad para desarrolladores — herramientas integradas vs MCP, exploración de codebase
- Escenario 5: Claude Code para CI/CD — bandera `-p`, aislamiento de sesión, prevención de duplicados
- Escenario 6: Extracción de datos estructurados — JSON schema, validación, self-correction, retry-with-feedback
- Escenario 7: Arquitectura de IA conversacional — gestión de contexto multi-turn, memoria, herramientas seguras, entradas ambiguas

### Día 24 — Antipatrones y tradeoffs: repaso final

- Antipatrones de agentic loop: parsear texto, límite arbitrario de iteraciones
- Antipatrones de herramientas: descripciones mínimas, herramientas monolíticas, truncado silencioso, errores genéricos
- Antipatrones de contexto: pasar contexto sin filtrar, acumulación de resultados irrelevantes
- Antipatrones de escalada: escalar por sentimiento, no escalar cuando política no cubre el caso
- Antipatrones de batch: procesar 50k documentos sin refinar prompt primero, enviar cada 6h con SLA de 30h
- Antipatrones de multiagente: subagentes sin contexto explícito, suprimir errores silenciosamente, abortar workflow completo por un fallo
- Tradeoffs clave del examen: hooks vs prompts, batch vs sincrónico, planning mode vs ejecución directa, chaining vs agentes dinámicos, `.claude/rules/` con paths vs CLAUDE.md de directorio
- Principios transversales: determinístico > probabilístico para reglas críticas, estructurado > texto libre para integración, explícito > implícito para contexto de subagentes

### Día 25 — Simulacro de examen y revisión final

- Simulacro completo con preguntas tipo examen de los 5 dominios
- Revisión de respuestas incorrectas
- Repaso de los "exam takeaways" de cada pregunta del README
- Confirmación de cobertura de todos los escenarios posibles
- Estrategia para el día del examen: responder todas las preguntas (sin penalización por adivinar), leer opciones incorrectas para entender por qué son incorrectas

---

## Recursos de referencia rápida

| Recurso | Cuándo consultar |
|---|---|
| `guide_es.md` / `guide_en.md` | Teoría completa por capítulo |
| `README.md` del repositorio | Preguntas tipo examen con explicaciones |
| `another_examen_topics.txt` | Subdomains 5.3–5.6: errores multiagente, contexto, provenance |
| Documentación oficial Messages API | Estructura de solicitud, `stop_reason` |
| Documentación oficial Tool Use | Definición de herramientas, `tool_choice` |
| Documentación oficial Message Batches | Batch API, `custom_id`, SLA |
| Documentación oficial Agent SDK | Hooks, subagentes, sesiones |
| Documentación oficial MCP | Tools, Resources, Servers |
| Documentación oficial Claude Code | CLAUDE.md, Skills, CI/CD, headless |
