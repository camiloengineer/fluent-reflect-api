import os
import requests
import json
from app.models.schemas import ChatMessage
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_headers():
    """Get OpenAI headers with proper authentication"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")

    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

SYSTEM_PROMPT = """Eres Nemesis, un entrevistador de código especializado en generar ejercicios de programación. Tu misión principal es mantener el flujo centrado en practicar, nunca en entregar soluciones listas.

ACTITUD (quirúrgico):
- Voz de ENTREVISTADOR. Directo, conciso y desafiante. Evita tono condescendiente o de helpdesk.
- Frases cortas orientadas a acción. Sin small talk.
- Prohibido usar: "¿En qué puedo ayudarte hoy?" o equivalentes.
- Empieza SIEMPRE cada respuesta con la frase "Hola, soy Nemesis" y continúa de forma natural después de esa frase.
- El único nombre válido es **Nemesis**. Nunca te presentes con otro nombre ni aceptes apodos distintos; si el usuario propone otro, reafirma que eres Nemesis y continúa.

OFERTA INICIAL SIN EJERCICIO ACTIVO:
- Propón un único ejercicio alineado con la intención del usuario (no listes más de uno a la vez).
- Describe en una frase qué evalúa y la dificultad aproximada.
- Aclara que aún está sin confirmar y pregunta si desea bloquearlo o explorar otra opción.
- Si el usuario duda o pide alternativas, presenta otra propuesta en la siguiente respuesta, PERO nunca uses la frase clave de confirmación.

CONFIRMACIÓN DEL RETO (único momento donde actúas):
- Si el usuario pide directamente («quiero», «hagamos», «asigname», «vamos con») un ejercicio específico, trátalo como confirmación inmediata.
- Cuando el usuario confirme explícitamente o pida directamente un reto específico, fija el ejercicio con la frase EXACTA `Ejercicio confirmado: <Nombre del ejercicio>` en una línea dedicada.
- Inmediatamente después, indica: `Haz clic en el botón "Generar ejercicio" para obtener el enunciado completo y avísame cuando lo tengas.`
- No vuelvas a preguntar si está seguro; la confirmación es definitiva salvo que el usuario cancele luego.
- Está prohibido entregar código, pseudo-código o soluciones completas antes de que el backend genere el reto. Limítate a explicar el objetivo y aclarar el próximo paso (generar el ejercicio).

SI YA HAY EJERCICIO ACTIVO:
- No propongas nuevos retos. Enfócate en apoyar con dudas, revisar código, dar pistas o feedback.
- Nunca uses la frase `Ejercicio confirmado:` mientras haya un ejercicio activo.

POSTERIOR A LA GENERACIÓN / FEEDBACK:
- Solo después de que el compilador ejecute código, evalúa calidad, eficiencia y estilo.
- Mantén la conversación centrada en progreso, no en soluciones cerradas.

FORMATO DE RESPUESTA:
- Usa Markdown.
- Resalta conceptos clave con **negritas**.
- Emplea `código inline` para nombres de funciones o variables.
- Evita bloques de código con soluciones antes de tiempo; únicamente utilízalos si el usuario comparte código para analizar.

RESTRICCIONES GENERALES:
- Nunca proporciones soluciones completas antes de que el usuario ejecute su código.
- Evita loops de confirmación; si el usuario insiste, responde una sola vez indicando que confirme con el botón.
- Mantén cada interacción orientada a un siguiente paso práctico.
- Estamos aquí para PROGRAMAR, no para charlar."""

async def chat_with_openai(
    messages: List[ChatMessage],
    language_name: str = "JavaScript",
    exercise_in_progress: bool = False,
    temperature: float = 0.5,
    max_tokens: int = 400,
    presence_penalty: float = 0,
    frequency_penalty: float = 0.2,
    top_p: float = 0.9,
    is_automatic: bool = False,
    current_code: str = "",
    exercise_name_snapshot: str = "",
    exercise_description_snapshot: str = "",
    execution_output: str = "",
    finished: bool = False
) -> str:
    """Chat with OpenAI GPT using the FluentReflect system prompt"""

    if finished and not is_automatic:
        raise ValueError("Finished verdict flow must be requested as an automatic prompt")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")

    # Prepare messages for OpenAI API
    openai_messages = []

    # Handle automatic prompts with special system prompts
    if is_automatic:
        from app.services.automatic_prompts_service import detect_automatic_prompt_type, get_automatic_system_prompt

        # Get the user message content to detect prompt type
        user_message_content = ""
        if messages and messages[-1].role == "user":
            user_message_content = messages[-1].content

        prompt_type = detect_automatic_prompt_type(user_message_content, finished)

        if prompt_type:
            # Use specialized system prompt for automatic prompts
            system_prompt = get_automatic_system_prompt(prompt_type, language_name, current_code, exercise_name_snapshot, execution_output)
            openai_messages.append({
                "role": "system",
                "content": system_prompt
            })

            # Inject deliberate reasoning flow for verdicts
            if prompt_type == "EXERCISE_VERDICT":
                from app.services.verdict_chain import build_verdict_reasoning_prompt

                reasoning_prompt = build_verdict_reasoning_prompt(
                    language_name=language_name,
                    exercise_name_snapshot=exercise_name_snapshot,
                    exercise_description_snapshot=exercise_description_snapshot,
                    current_code=current_code,
                    execution_output=execution_output,
                )

                openai_messages.append({
                    "role": "system",
                    "content": reasoning_prompt
                })
        else:
            # Fallback to normal system prompt if automatic prompt type not recognized
            system_prompt = f"{SYSTEM_PROMPT}\n\nIMPORTANTE: El usuario está trabajando con {language_name}."
            openai_messages.append({
                "role": "system",
                "content": system_prompt
            })
    else:
        # Normal system prompt for regular conversations
        language_specific_prompt = f"{SYSTEM_PROMPT}\n\nIMPORTANTE: El usuario está trabajando con {language_name}. Todos los ejemplos de código, explicaciones y soluciones deben estar basados en {language_name}."

        # Add current code context if available
        if current_code and current_code.strip():
            language_specific_prompt += f"\n\n📝 CÓDIGO ACTUAL EN EL EDITOR:\n```{language_name.lower()}\n{current_code}\n```\n\n🎯 INSTRUCCIONES IMPORTANTES:\n- SIEMPRE refiere a este código específico cuando el usuario pregunte\n- Analiza línea por línea lo que está implementado y lo que falta\n- Menciona elementos específicos del código (nombres de variables, funciones, comentarios)\n- Si hay comentarios como '// TU CÓDIGO AQUÍ', mencionalo directamente\n- Si hay test cases, analízalos y úsalos para explicar qué debería hacer la función"

        # Add exercise state context
        if exercise_in_progress:
            language_specific_prompt += "\n\n🎯 ESTADO ACTUAL: Hay un ejercicio en curso. NO ofrezcas nuevos ejercicios. Enfócate en ayudar con el ejercicio actual: responder preguntas, dar pistas, revisar código, etc."
        else:
            language_specific_prompt += "\n\n🚀 ESTADO ACTUAL: No hay ejercicio activo. Tu objetivo es SIEMPRE proponer ejercicios concretos. Si el usuario pregunta sobre conceptos, sugiere inmediatamente un ejercicio relacionado."

        # Add system prompt
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
        # Try GPT-5-mini first, fallback to standard chat endpoint if not available
        BASE_URL = "https://api.openai.com/v1/responses"
        headers = get_openai_headers()

        # Convert messages to the proper format for gpt-5-mini
        # Combine system and user messages into a single input string
        input_content = ""

        for msg in openai_messages:
            if msg["role"] == "system":
                input_content += f"SYSTEM: {msg['content']}\n\n"
            elif msg["role"] == "user":
                input_content += f"USER: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                input_content += f"ASSISTANT: {msg['content']}\n\n"

        # Remove trailing newlines
        input_content = input_content.strip()

        # Select reasoning effort with optional env override for verdict-only escalation
        reasoning_effort = "minimal"
        if is_automatic:
            # Best-effort detection: if the system prompt includes our verdict chain header, allow override
            env_override = os.getenv("VERDICT_REASONING_EFFORT", "").strip().lower()
            if env_override in {"minimal", "low"}:
                reasoning_effort = env_override

        payload = {
            "model": "gpt-5-mini",
            "input": input_content,
            "max_output_tokens": max(max_tokens, 300),  # Ensure minimum tokens for response (benchmark-backed)
            "truncation": "auto",
            "reasoning": {"effort": reasoning_effort}  # Minimal by default; allow low via env for verdicts
        }

        response = requests.post(
            BASE_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=60
        )

        if response.status_code == 404 or response.status_code == 401:
            # Fallback to standard chat/completions endpoint with gpt-4
            fallback_url = "https://api.openai.com/v1/chat/completions"
            fallback_payload = {
                "model": "gpt-4",
                "messages": openai_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "presence_penalty": presence_penalty,
                "frequency_penalty": frequency_penalty,
                "top_p": top_p
            }

            response = requests.post(
                fallback_url,
                headers=headers,
                data=json.dumps(fallback_payload),
                timeout=60
            )

        response.raise_for_status()
        data = response.json()

        # Handle GPT-5 response format
        if "output" in data:
            texts = []
            for item in data.get("output", []):
                if item.get("type") == "message":
                    for part in item.get("content", []):
                        if part.get("type") == "output_text":
                            texts.append(part.get("text", ""))

            result_text = "\n".join(texts)
        else:
            # Handle standard chat/completions response format
            result_text = data["choices"][0]["message"]["content"]

        if not result_text:
            raise Exception("No valid response text found in API response")

        return result_text

    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP request error: {str(e)}")
    except Exception as e:
        raise Exception(f"API error: {str(e)}")
