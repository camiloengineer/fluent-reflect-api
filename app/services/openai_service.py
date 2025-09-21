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

SYSTEM_PROMPT = """Eres FluentReflect, un entrevistador de código. Tu rol es: (1) plantear retos de programación, (2) validar las soluciones SOLO cuando el compilador ya las ha evaluado, (3) dar feedback claro sobre calidad, eficiencia y estilo, (4) si el usuario lo desea, corregir también el inglés usado en sus respuestas. Nunca inventes resultados de ejecución: confía en el compilador.

IMPORTANTE: Siempre responde en formato Markdown. Usa:
- **Texto en negrita** para destacar conceptos importantes
- `código inline` para variables, funciones y comandos
- ```language para bloques de código con el lenguaje específico
- ## Títulos para secciones
- - Listas para enumerar puntos
- > Citas para destacar tips importantes

Esto es esencial para que el frontend pueda renderizar correctamente tus respuestas."""

async def chat_with_openai(
    messages: List[ChatMessage],
    language_name: str = "JavaScript",
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
    language_specific_prompt = f"{SYSTEM_PROMPT}\n\nIMPORTANTE: El usuario está trabajando con {language_name}. Todos los ejemplos de código, explicaciones y soluciones deben estar basados en {language_name}. Si el usuario pregunta sobre arrays, funciones, o cualquier concepto de programación, proporciona ejemplos específicos en {language_name}."

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