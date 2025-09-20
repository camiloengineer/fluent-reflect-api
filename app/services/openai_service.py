import os
from openai import OpenAI
from app.models.schemas import ChatMessage
from typing import List

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = """Eres FluentReflect, un entrevistador de código. Tu rol es: (1) plantear retos de programación, (2) validar las soluciones SOLO cuando el compilador ya las ha evaluado, (3) dar feedback claro sobre calidad, eficiencia y estilo, (4) si el usuario lo desea, corregir también el inglés usado en sus respuestas. Nunca inventes resultados de ejecución: confía en el compilador."""

async def chat_with_openai(
    messages: List[ChatMessage],
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

    # Always add system prompt first
    openai_messages.append({
        "role": "system",
        "content": SYSTEM_PROMPT
    })

    # Add user messages
    for message in messages:
        openai_messages.append({
            "role": message.role,
            "content": message.content
        })

    try:
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