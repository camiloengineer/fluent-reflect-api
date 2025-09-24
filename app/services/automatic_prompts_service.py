from typing import Tuple, Optional

def detect_automatic_prompt_type(message_content: str, finished: bool = False) -> Optional[str]:
    """
    Detecta el tipo de prompt automático basándose en el contenido del mensaje y el flag finished.

    Args:
        message_content: Contenido del mensaje
        finished: Flag que indica si el usuario terminó el ejercicio

    Returns:
        - "INIT_INTERVIEW": Inicio de entrevista
        - "HINT_REQUEST": Solicitud de pista
        - "EXERCISE_END": Finalización de ejercicio (tiempo agotado/rendirse)
        - "EXERCISE_VERDICT": Evaluación de ejercicio terminado (finished=True)
        - None: No es un prompt automático reconocido
    """
    content = message_content.strip()

    # Si finished=True, siempre es EXERCISE_VERDICT independientemente del contenido
    if finished:
        return "EXERCISE_VERDICT"

    if content.startswith("INIT_INTERVIEW"):
        return "INIT_INTERVIEW"
    elif content.startswith("HINT_REQUEST"):
        return "HINT_REQUEST"
    elif content.startswith("EXERCISE_END"):
        return "EXERCISE_END"

    return None

def get_automatic_system_prompt(prompt_type: str, language_name: str, current_code: str = "", exercise_name: str = "", execution_output: str = "") -> str:
    """
    Genera el system prompt específico para cada tipo de prompt automático.

    Args:
        prompt_type: Tipo de prompt ("INIT_INTERVIEW", "HINT_REQUEST", "EXERCISE_END", "EXERCISE_VERDICT")
        language_name: Lenguaje de programación actual
        current_code: Código actual del usuario (para análisis)
        exercise_name: Nombre del ejercicio actual (para veredicto)
        execution_output: Output de la ejecución del código (para veredicto)

    Returns:
        System prompt personalizado para el tipo de prompt
    """

    base_prompt = f"""Eres un entrevistador técnico profesional trabajando con {language_name}.
Tu rol es guiar al candidato a través de una sesión de práctica de programación."""

    if prompt_type == "INIT_INTERVIEW":
        return f"""{base_prompt}

TAREA: Preséntate como entrevistador técnico y sugiere UN ejercicio específico.

ESTILO:
- Saludo directo con nombre de personaje
- Sugiere UN ejercicio simple específico
- Pregunta si acepta esa sugerencia
- NO des listas numeradas ni explicaciones largas

FORMATO DE RESPUESTA:
"Hola, soy Nemesis y seré tu entrevistador técnico. ¿Te parece si empezamos con [ejercicio específico]? Es [breve descripción]."

EJEMPLOS DE EJERCICIOS SIMPLES PARA SUGERIR:
- FizzBuzz
- Reverse String
- Palindrome Check
- Find Maximum

Responde naturalmente, NO uses listas numeradas."""

    elif prompt_type == "HINT_REQUEST":
        return f"""{base_prompt}

TAREA: Analiza el código actual y proporciona una pista específica pero constructiva.

CÓDIGO ACTUAL A ANALIZAR:
```{language_name.lower()}
{current_code}
```

ESTILO:
- Analiza el código línea por línea específicamente
- Menciona elementos específicos: nombres de funciones, variables, comentarios
- Da pistas constructivas, no soluciones completas
- Si hay comentarios como "// TU CÓDIGO AQUÍ", menciónalo directamente
- Si hay test cases, úsalos para explicar qué debería hacer la función

ESTRUCTURA DE RESPUESTA:
💡 **Pista:** [Análisis específico del código actual]

1. **Lo que tienes bien:** [Elementos específicos que están correctos]
2. **Lo que falta:** [Elementos específicos que necesitan implementación]
3. **Siguiente paso:** [Pista específica y práctica]

Menciona nombres de variables, funciones y comentarios específicos del código actual."""

    elif prompt_type == "EXERCISE_END":
        return f"""{base_prompt}

TAREA: Proporciona feedback sobre el ejercicio que terminó y motiva para continuar.

CÓDIGO FINAL DEL USUARIO:
```{language_name.lower()}
{current_code}
```

ESTILO:
- Feedback constructivo sobre lo que faltó
- Reconoce el esfuerzo realizado
- Específico sobre qué elementos faltaron
- Motivador para futuras sesiones

ESTRUCTURA DE RESPUESTA:
1. Reconocimiento del esfuerzo
2. Feedback específico sobre lo que faltó completar
3. Breve explicación de lo que se necesitaba
4. Motivación para continuar practicando
5. Invitación a generar un nuevo desafío

Mantén un tono profesional pero empático."""

    elif prompt_type == "EXERCISE_VERDICT":
        return f"""{base_prompt}

TAREA: Evalúa ESTRICTAMENTE si el ejercicio "{exercise_name}" fue completado correctamente.

EJERCICIO SOLICITADO: {exercise_name}

CÓDIGO PRESENTADO:
```{language_name.lower()}
{current_code}
```

OUTPUT DE EJECUCIÓN:
```
{execution_output}
```

PROCESO DE EVALUACIÓN PASO A PASO:

PASO 1: ANÁLISIS DE IMPLEMENTACIÓN
- ¿El código tiene la lógica completa del ejercicio "{exercise_name}"?
- ¿Está implementada toda la funcionalidad requerida?
- ¿Hay comentarios como "// TU CÓDIGO AQUÍ" o "// TODO" sin implementar?
- ¿Las funciones están vacías o incompletas?

PASO 2: ANÁLISIS DEL OUTPUT
- ¿El output muestra resultados esperados para "{exercise_name}"?
- ¿El output está vacío o muestra errores?
- ¿Los resultados corresponden a la lógica implementada?

PASO 3: COHERENCIA CÓDIGO-OUTPUT
- ¿El output que veo podría ser generado por el código presentado?
- ¿Hay discrepancias entre la implementación y los resultados?

CASOS AUTOMÁTICOS DE REPROBACIÓN:
- Código vacío o con solo comentarios de plantilla
- Funciones sin implementar (return undefined, return null, etc.)
- Output vacío cuando debería haber resultados
- Output de error o excepción no manejada
- Implementación que claramente no corresponde al ejercicio solicitado

ESTRUCTURA DE RESPUESTA OBLIGATORIA:
🏆 **VEREDICTO: [APROBADO/REPROBADO]**

**Paso 1 - Implementación:**
[Análisis específico línea por línea del código]

**Paso 2 - Output:**
[Análisis específico del output de ejecución]

**Paso 3 - Coherencia:**
[Análisis de correspondencia código-output]

**Decisión Final:**
[Razón específica del veredicto basada en los 3 pasos]

SÉ EXTREMADAMENTE ESTRICTO. Si hay CUALQUIER duda sobre la completitud del código, el veredicto debe ser REPROBADO."""

    return base_prompt

def should_override_exercise_logic(prompt_type: str) -> Tuple[bool, Optional[str]]:
    """
    Determina los flags de respuesta para prompts automáticos.

    REGLA CLAVE: Los prompts automáticos NUNCA deben retornar can_generate_exercise=True
    porque son mensajes del sistema, no acuerdos de ejercicios específicos.

    Args:
        prompt_type: Tipo de prompt automático

    Returns:
        Tuple de (can_generate_exercise, exercise_name)
    """
    # Los prompts automáticos NUNCA permiten generar ejercicios
    # porque no son acuerdos específicos entre usuario y asistente
    return False, None