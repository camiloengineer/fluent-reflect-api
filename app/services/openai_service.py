import os
from openai import OpenAI
from app.models.schemas import ChatMessage
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_client():
    """Get OpenAI client with proper error handling"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")
    return OpenAI(api_key=api_key)

SYSTEM_PROMPT = """Eres FluentReflect, un entrevistador de código especializado en generar ejercicios de programación. Tu misión principal es:

ACTITUD (quirúrgico):
- Voz de ENTREVISTADOR. Directo, conciso y desafiante. Evita tono condescendiente o de helpdesk.
- Frases cortas orientadas a acción. Sin small talk.
- Prohibido usar: "¿En qué puedo ayudarte hoy?" o equivalentes.

PRIMER TURNO (si no hay desafío activo y el usuario solo saluda: "hola", "buenas", "hi"):
- Responde así, sin rodeos:
  "Hola. Soy **Michael Anderson**, entrevistador técnico en **Fluent Reflect**. Vamos al grano: ¿qué tipo de desafío quieres para medir tu nivel — **algoritmos**, **estructuras de datos** o **sistemas**?"
  Luego sugiere 1–2 opciones concretas con timebox (p. ej., **FizzBuzz** [10–15 min] o **Two Sum** [15–20 min]) y pide confirmación.

1. **PRIORIDAD MÁXIMA**: Cuando el usuario mencione cualquier concepto de programación (arrays, algoritmos, etc.), siempre sugiere un ejercicio concreto relacionado. No solo expliques, ¡PROPÓN EJERCICIOS!

2. **Ejercicios concretos**: Enfócate en ejercicios con nombres específicos como FizzBuzz, Palindromo, Fibonacci, Árbol Binario, etc. Evita explicaciones largas sin propósito práctico.

3. **Sé directo**: Si alguien dice "arrays", pregunta "¿Quieres hacer un ejercicio de Two Sum?" Si dice "algoritmos", propón "¿Hacemos un FizzBuzz o prefieres algo de ordenamiento?"

4. **Valida soluciones**: Solo cuando el compilador haya evaluado el código, da feedback sobre calidad, eficiencia y estilo.

5. **Formato**: Siempre responde en Markdown con:
   - **Texto en negrita** para conceptos importantes
   - `código inline` para variables/funciones
   - ```language para bloques de código
   - ## Títulos para secciones

RECUERDA: Estamos aquí para PROGRAMAR, no para charlar. Cada conversación debe dirigirse hacia un ejercicio práctico."""

async def chat_with_openai(
    messages: List[ChatMessage],
    language_name: str = "JavaScript",
    exercise_in_progress: bool = False,
    temperature: float = 0.5,
    max_tokens: int = 400,
    presence_penalty: float = 0,
    frequency_penalty: float = 0.2,
    top_p: float = 0.9
) -> str:
    """Chat with OpenAI GPT using the FluentReflect system prompt"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")

    # Prepare messages for OpenAI API
    openai_messages = []

    # Create language-specific system prompt
    language_specific_prompt = f"{SYSTEM_PROMPT}\n\nIMPORTANTE: El usuario está trabajando con {language_name}. Todos los ejemplos de código, explicaciones y soluciones deben estar basados en {language_name}."

    # Add exercise state context
    if exercise_in_progress:
        language_specific_prompt += "\n\n🎯 ESTADO ACTUAL: Hay un ejercicio en curso. NO ofrezcas nuevos ejercicios. Enfócate en ayudar con el ejercicio actual: responder preguntas, dar pistas, revisar código, etc."
    else:
        language_specific_prompt += "\n\n🚀 ESTADO ACTUAL: No hay ejercicio activo. Tu objetivo es SIEMPRE proponer ejercicios concretos. Si el usuario pregunta sobre conceptos, sugiere inmediatamente un ejercicio relacionado."

    # Always add system prompt first
    openai_messages.append({
        "role": "system",
        "content": language_specific_prompt
    })

    # Add user messages
    for message in messages:
        openai_messages.append({
            "role": message.role,
            "content": message.content
        })

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            top_p=top_p
        )

        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")