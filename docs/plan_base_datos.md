
---

# 1. Enfoque general de la app

La app no dependerá de inteligencia artificial para generar ejercicios, sino de una **base de datos estructurada** que permita:

* entregar un ejercicio diario de forma aleatoria
* respetar el nivel CEFR del usuario
* variar el tipo de reto
* mantener una progresión pedagógica coherente
* crecer fácilmente con nuevos ejercicios y niveles

La lógica del producto debe estar basada en una **arquitectura de práctica de writing**, no en una lista suelta de prompts.

---

# 2. Objetivo de la base de datos

Construir una base que permita organizar ejercicios diarios de writing en inglés para estudiantes de distintos niveles, comenzando por:

* **A1**
* **A2**
* **B1**

Más adelante la arquitectura podrá escalar a:

* B2
* C1
* C2

---

# 3. Qué significa “arquitectura de práctica de writing”

La base debe almacenar no solo el texto del ejercicio, sino también la lógica pedagógica detrás.

Cada ejercicio debe responder a estas preguntas:

1. **Qué tipo de writing practica**
2. **Qué habilidad desarrolla**
3. **Qué nivel CEFR requiere**
4. **Qué restricción incluye**
5. **Qué resultado espera del estudiante**
6. **Cómo rota dentro del sistema para evitar repetición**

Eso convierte la app en una herramienta real de aprendizaje.

---

# 4. Arquitectura conceptual de la práctica de writing

La arquitectura puede organizarse en 5 capas.

## Capa 1: Nivel CEFR

Filtra los ejercicios según el dominio del usuario.

* A1
* A2
* B1

## Capa 2: Tipo de ejercicio

Define la naturaleza del reto.

* opinion
* quick response
* compare and choose
* storytelling
* reformulation
* journaling
* email
* summary
* description
* debate
* counterargument
* rewrite challenge
* vocabulary mission
* error hunt
* reflection
* scenario writing

## Capa 3: Objetivo de aprendizaje

Qué habilidad de writing se entrena.

* sentence building
* idea organization
* basic coherence
* grammar control
* vocabulary usage
* tone adaptation
* argumentation
* descriptive writing
* narrative writing
* functional writing
* reflective writing

## Capa 4: Restricción

La condición que obliga al estudiante a practicar mejor.

* use past simple
* use present perfect
* defend one side
* write 5 sentences
* include 2 reasons
* do not use “good” or “nice”
* use these 4 words
* write in email format
* compare two options
* include one surprise ending

## Capa 5: Formato de salida

Qué debe entregar el estudiante.

* 3 sentences
* short paragraph
* 5-sentence paragraph
* email
* mini journal
* comparison paragraph
* corrected text
* short story
* summary

---

# 5. Estructura maestra de la base de datos

La recomendación es usar una estructura lógica de tablas relacionadas.

---

## Tabla 1: `levels`

Define los niveles CEFR.

Campos:

* `level_id`
* `level_code` → A1 / A2 / B1
* `level_name`
* `description`
* `active`

### Ejemplo

* 1 | A1 | Beginner
* 2 | A2 | Elementary
* 3 | B1 | Intermediate

---

## Tabla 2: `exercise_types`

Catálogo de tipos de ejercicio.

Campos:

* `exercise_type_id`
* `name`
* `description`
* `default_output_format`
* `active`

### Ejemplo

* 1 | Opinion
* 2 | Quick Response
* 3 | Storytelling
* 4 | Rewrite Challenge
* 5 | Compare and Choose
* 6 | Email
* 7 | Description
* 8 | Reflection

---

## Tabla 3: `skill_focus`

Habilidades de writing que se trabajan.

Campos:

* `skill_focus_id`
* `name`
* `description`

### Ejemplo

* 1 | Fluency
* 2 | Accuracy
* 3 | Coherence
* 4 | Vocabulary Range
* 5 | Argumentation
* 6 | Tone Control
* 7 | Narrative Writing
* 8 | Functional Writing

---

## Tabla 4: `constraint_types`

Tipos generales de restricciones.

Campos:

* `constraint_type_id`
* `name`
* `description`

### Ejemplo

* 1 | Grammar
* 2 | Vocabulary
* 3 | Structure
* 4 | Tone
* 5 | Creativity
* 6 | Limitation

---

## Tabla 5: `constraints`

Restricciones concretas.

Campos:

* `constraint_id`
* `constraint_type_id`
* `name`
* `description`
* `level_id`
* `active`

### Ejemplos

* Use present simple
* Use past simple
* Use 3 adjectives
* Defend one side
* Write 5 sentences
* Use these 4 words
* Do not use “good” or “nice”
* Write in email format
* Include one question
* Use because at least twice

---

## Tabla 6: `topics`

Temas sobre los que escribe el estudiante.

Campos:

* `topic_id`
* `name`
* `description`
* `active`

### Ejemplos

* Daily life
* Family
* School
* Work
* Hobbies
* Food
* Travel
* Technology
* Feelings
* Future plans
* Personal habits
* My city

---

## Tabla 7: `output_formats`

Formatos esperados.

Campos:

* `output_format_id`
* `name`
* `description`

### Ejemplos

* 3 sentences
* 5 sentences
* short paragraph
* email
* mini journal
* short comparison
* mini story
* corrected version

---

## Tabla 8: `exercises`

Tabla central de ejercicios.

Campos recomendados:

* `exercise_id`
* `title`
* `instructions`
* `level_id`
* `exercise_type_id`
* `topic_id`
* `output_format_id`
* `difficulty_score`
* `word_count_min`
* `word_count_max`
* `estimated_time_minutes`
* `tone`
* `rotation_group`
* `pedagogical_goal`
* `grammar_focus`
* `writing_function`
* `is_active`
* `created_at`
* `updated_at`

---

## Tabla 9: `exercise_constraints`

Un ejercicio puede tener una o varias restricciones.

Campos:

* `exercise_constraint_id`
* `exercise_id`
* `constraint_id`

---

## Tabla 10: `exercise_skills`

Un ejercicio puede trabajar varias habilidades.

Campos:

* `exercise_skill_id`
* `exercise_id`
* `skill_focus_id`

---

## Tabla 11: `example_answers`

Opcional, pero muy útil.

Campos:

* `example_answer_id`
* `exercise_id`
* `sample_text`
* `notes`

Sirve para el equipo académico, calidad y revisión.

---

## Tabla 12: `evaluation_criteria`

Para corrección, scoring o seguimiento futuro.

Campos:

* `evaluation_criteria_id`
* `exercise_id`
* `criterion_name`
* `description`

Ejemplos:

* grammar accuracy
* clarity
* task completion
* vocabulary use
* coherence

---

# 6. Estructura mínima viable

Si quieren empezar rápido, pueden arrancar con:

* `levels`
* `exercise_types`
* `constraints`
* `topics`
* `output_formats`
* `exercises`
* `exercise_constraints`

Eso ya permite operar la app.

---

# 7. Cómo debe verse un ejercicio dentro de la base

## Ejemplo 1

**Title:** My morning routine
**Level:** A1
**Type:** Description
**Topic:** Daily life
**Instructions:** Write about your morning routine.
**Constraint:** Use present simple and write 5 sentences.
**Output format:** 5 sentences
**Word count:** 30–50
**Time:** 5 min
**Skill focus:** sentence building, basic coherence

---

## Ejemplo 2

**Title:** Study with books or videos
**Level:** A2
**Type:** Compare and Choose
**Topic:** Learning
**Instructions:** Would you rather learn English by watching videos or reading books? Choose one and explain why.
**Constraint:** Give 2 reasons and use because at least twice.
**Output format:** Short paragraph
**Word count:** 60–80
**Time:** 8 min
**Skill focus:** coherence, opinion, vocabulary use

---

## Ejemplo 3

**Title:** An unexpected day
**Level:** B1
**Type:** Storytelling
**Topic:** Daily life
**Instructions:** Write a short story about an unexpected day.
**Constraint:** Use past simple and include one surprise ending.
**Output format:** Mini story
**Word count:** 80–120
**Time:** 10 min
**Skill focus:** narrative writing, grammar control

---

# 8. Lógica para entregar ejercicios diarios aleatorios

La selección no debería ser azar puro.
Debería ser **aleatoriedad controlada**.

## Reglas sugeridas

1. Filtrar por nivel CEFR del usuario
2. Excluir ejercicios ya usados recientemente
3. Rotar tipos para no repetir varios días seguidos
4. Variar también el tema
5. Mantener una dificultad adecuada para el nivel

---

## Ejemplo de lógica diaria

Si el usuario es A2:

* buscar ejercicios activos de nivel A2
* excluir ejercicios completados en los últimos 20 o 30 días
* priorizar tipos no vistos recientemente
* seleccionar uno aleatoriamente entre los elegibles

---

## Rotación semanal sugerida

Para que el “daily challenge” sí se sienta distinto:

* Lunes: quick response
* Martes: opinion
* Miércoles: description
* Jueves: rewrite / reformulation
* Viernes: compare and choose
* Sábado: storytelling / journaling
* Domingo: reflection / error hunt

La rotación puede convivir con aleatoriedad interna.

---

# 9. Cómo estructurar los ejercicios por nivel CEFR

## Nivel A1

### Objetivo

* construir frases simples
* describir rutinas y preferencias
* responder ideas muy concretas
* usar vocabulario básico frecuente
* expresar gustos, hábitos y datos personales

### Tipos ideales

* quick response
* description
* basic opinion
* vocabulary mission
* simple journaling

### Restricciones adecuadas

* write 3 sentences
* use present simple
* use I like / I don’t like
* use 3 adjectives
* answer with because

### Producción esperada

* frases cortas
* párrafos muy breves
* alta estructura guiada

---

## Nivel A2

### Objetivo

* conectar ideas con más claridad
* justificar opiniones
* comparar opciones
* describir experiencias simples
* escribir párrafos cortos con mejor organización

### Tipos ideales

* opinion
* compare and choose
* rewrite challenge
* simple email
* reflection
* scenario writing

### Restricciones adecuadas

* give 2 reasons
* use past simple
* use because / but / so
* write 60–80 words
* include one example

### Producción esperada

* párrafos cortos
* mensajes funcionales simples
* ideas conectadas de forma básica

---

## Nivel B1

### Objetivo

* escribir con mayor autonomía
* narrar experiencias
* defender una postura sencilla
* resumir y reformular
* usar una variedad mayor de estructuras
* escribir textos funcionales y personales con más claridad

### Tipos ideales

* debate
* storytelling
* reformulation
* summary
* scenario writing
* structured email
* reflection
* counterargument básico

### Restricciones adecuadas

* defend one side
* include a counter idea
* use past simple and present perfect
* write 80–120 words
* add a conclusion sentence

### Producción esperada

* párrafos bien organizados
* historias breves
* opiniones justificadas
* emails más completos

---

# 10. Campos importantes para mantener la arquitectura pedagógica

Estos campos son clave porque le dan inteligencia estructural a la base, aunque la app no use IA.

## Campo: `pedagogical_goal`

Describe qué busca lograr el ejercicio.

Ejemplos:

* Build simple sentences
* Practice daily routine vocabulary
* Express basic opinion
* Compare two ideas
* Narrate a past event
* Write a functional message

## Campo: `grammar_focus`

Ejemplos:

* present simple
* past simple
* there is / there are
* can / can’t
* adjectives
* comparatives
* basic connectors
* present perfect

## Campo: `writing_function`

Qué función comunicativa cumple.

Ejemplos:

* describe
* explain
* compare
* justify
* narrate
* request
* apologize
* reflect
* summarize

## Campo: `rotation_group`

Sirve para la lógica diaria.

Ejemplos:

* daily_opinion
* daily_description
* daily_story
* daily_rewrite
* daily_reflection

---

# 11. Estructura ideal de cada registro de ejercicio

Cada ejercicio debería tener:

* **ID**
* **Título**
* **Nivel CEFR**
* **Tipo**
* **Tema**
* **Objetivo pedagógico**
* **Instrucción principal**
* **Restricción**
* **Formato esperado**
* **Rango de palabras**
* **Tiempo estimado**
* **Foco gramatical**
* **Habilidad principal**
* **Función de writing**
* **Grupo de rotación**
* **Activo / inactivo**

---

# 12. Ejemplo de catálogo inicial para poblar la base

Yo sugiero empezar así:

## A1

* 25 ejercicios

## A2

* 35 ejercicios

## B1

* 40 ejercicios

**Total inicial: 100 ejercicios**

Eso ya da buena variedad para una primera versión.

---

# 13. Distribución recomendada por tipo

## A1

* Quick response: 6
* Description: 6
* Simple opinion: 4
* Vocabulary mission: 4
* Reflection/journaling simple: 5

## A2

* Opinion: 6
* Compare and choose: 6
* Description: 5
* Rewrite challenge: 5
* Email/scenario: 6
* Reflection: 4
* Vocabulary mission: 3

## B1

* Opinion/debate: 8
* Storytelling: 6
* Reformulation: 5
* Scenario writing: 6
* Summary: 4
* Email: 4
* Counterargument: 3
* Reflection: 4

---

# 14. Ejemplo de estructura tabular simple

| exercise_id | title | level | type | topic | instructions | constraint | output_format | word_min | word_max | grammar_focus | pedagogical_goal |
|---|---|---|---|---|---|---|---:|---:|---|---|
| 1 | My favorite food | A1 | Description | Food | Describe your favorite food. | Use 4 adjectives. | 5 sentences | 30 | 50 | Present simple | Basic description |
| 2 | Books or videos? | A2 | Compare and Choose | Study | Choose one and explain why. | Give 2 reasons. | Short paragraph | 60 | 80 | Because / but | Comparison |
| 3 | A strange day | B1 | Storytelling | Daily life | Write about a strange day. | Use past simple and one surprise. | Mini story | 80 | 120 | Past simple | Narrative writing |

---

# 15. Qué no debería faltar en la app aunque no use IA

Aunque no tenga IA, la app debería considerar:

* historial de ejercicios realizados
* filtro por nivel CEFR
* filtro por tipo de ejercicio
* aleatoriedad controlada
* progresión pedagógica
* opción de marcar completado
* favoritos o guardados
* posibilidad futura de corrección manual o automática

---

# 16. Recomendación de diseño funcional

Yo estructuraría la app así:

## Modo 1: Daily Challenge

El usuario entra y recibe 1 ejercicio del día.

## Modo 2: Practice by Category

Puede practicar por tipo:

* opinion
* email
* storytelling
* reflection
* description

## Modo 3: Practice by Grammar

Puede practicar por foco gramatical:

* present simple
* past simple
* comparatives
* present perfect

Así la base sirve para más que solo el reto diario.

---

# 17. Recomendación más importante

Antes de cargar ejercicios, conviene definir una **taxonomía cerrada**.

Es decir, dejar fijado desde el inicio:

* qué niveles existirán
* qué tipos de ejercicios existirán
* qué restricciones existirán
* qué formatos de salida existirán
* qué temas existirán
* qué funciones de writing existirán

Porque si empiezan cargando ejercicios sin ese catálogo maestro, la base se vuelve inconsistente muy rápido.

---

# 18. Propuesta de siguientes entregables

Los siguientes entregables correctos serían:

## Entregable 1

**Diccionario de base de datos**
Con tablas, campos y definiciones.

## Entregable 2

**Catálogo maestro de tipos, restricciones, temas y formatos**
Para mantener consistencia.

## Entregable 3

**Primer lote de ejercicios A1, A2 y B1**
Idealmente 100 registros.

## Entregable 4

**Reglas de selección aleatoria diaria**
Para implementación técnica.

---

# 19. Definición en una sola frase

La app debe apoyarse en una **base de datos estructurada de práctica de writing alineada al CEFR**, organizada por nivel, tipo de ejercicio, objetivo pedagógico, restricción, tema, función comunicativa y formato de salida, para entregar retos diarios aleatorios con variedad, coherencia y progresión de aprendizaje.

---