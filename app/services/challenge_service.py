import os
import uuid
from openai import OpenAI
from typing import Optional

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

CHALLENGE_GENERATION_PROMPT = """You are a programming challenge generator for technical interviews.

{context_instruction}

Generate a programming challenge with these specifications:
- Language: {language}
- Difficulty: {difficulty}
- Topic: {topic}

You must respond EXACTLY in this JSON format (no markdown, no extra explanations):

{{
  "title": "Concise challenge title",
  "description": "Clear problem description in Spanish. Explain what the function should do.",
  "function_name": "functionName",
  "function_signature": "function functionName(param1, param2)",
  "test_cases": [
    {{"input": "example parameters", "expected": "expected result", "explanation": "Why this result"}},
    {{"input": "example parameters 2", "expected": "expected result 2", "explanation": "Why this result"}}
  ]
}}

Requirements:
- Challenge must be appropriate for technical interviews
- Include 3-4 diverse test cases
- Function should be implementable in 10-15 lines of code
- If no topic specified, choose one appropriate for the difficulty"""

CONTEXT_ANALYSIS_PROMPT = """Analyze this chat conversation to understand what programming challenge was discussed or agreed upon.

CHAT CONVERSATION:
{chat_context}

Extract:
1. What specific challenge/problem was mentioned (FizzBuzz, arrays, algorithms, etc.)
2. Any specific requirements or constraints discussed
3. Difficulty level mentioned or implied

Based on this conversation, I need to generate a challenge that matches EXACTLY what was discussed.
If no specific challenge was mentioned, suggest an appropriate one for the language and context."""

async def generate_challenge(
    language: str = "javascript",
    difficulty: str = "easy",
    topic: Optional[str] = None,
    chat_context: Optional[list] = None
) -> dict:
    """Generate a programming challenge using OpenAI"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")

    # Analyze chat context if provided
    context_instruction = ""
    if chat_context and len(chat_context) > 0:
        context_instruction = await analyze_chat_context(chat_context, language)
    else:
        context_instruction = "Generate a random appropriate challenge for the given parameters."

    # Format the prompt with parameters
    prompt = CHALLENGE_GENERATION_PROMPT.format(
        context_instruction=context_instruction,
        language=language,
        difficulty=difficulty,
        topic=topic or "algorithms"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Generate a {difficulty} challenge in {language} based on the conversation context."}
            ],
            temperature=0.7,
            max_tokens=800
        )

        challenge_json = response.choices[0].message.content

        # Parse the JSON response
        import json
        challenge_data = json.loads(challenge_json)

        # Generate template code
        template_code = generate_template_code(challenge_data, language)

        return {
            "challenge_id": str(uuid.uuid4()),
            "title": challenge_data["title"],
            "description": challenge_data["description"],
            "template_code": template_code
        }

    except Exception as e:
        raise Exception(f"Challenge generation failed: {str(e)}")

def generate_template_code(challenge_data: dict, language: str) -> str:
    """Generate the template code that users will see in the editor"""

    if language.lower() == "javascript":
        return generate_javascript_template(challenge_data)
    elif language.lower() == "python":
        return generate_python_template(challenge_data)
    else:
        raise Exception(f"Language {language} not supported yet")

def generate_javascript_template(challenge_data: dict) -> str:
    """Generate JavaScript template with function signature and test cases"""

    function_name = challenge_data.get("function_name", "solution")
    test_cases = challenge_data.get("test_cases", [])

    # Clean up function signature if it has extra braces
    signature = challenge_data.get("function_signature", f"function {function_name}()")
    if signature.endswith(" { }"):
        signature = signature[:-4]  # Remove " { }"
    elif signature.endswith(" {}"):
        signature = signature[:-3]  # Remove " {}"

    template = f'''/**
 * Problem: {challenge_data["title"]}
 *
 * {challenge_data["description"]}
 */
{signature} {{
  // ✍️ TU CÓDIGO AQUÍ

}}

// Test Cases (ejecutables)'''

    for i, test_case in enumerate(test_cases):
        template += f'''
console.log({function_name}({test_case["input"]})); // Esperado: {test_case["expected"]}'''

    return template

def generate_python_template(challenge_data: dict) -> str:
    """Generate Python template with function signature and test cases"""

    function_name = challenge_data.get("function_name", "solution")
    test_cases = challenge_data.get("test_cases", [])

    # Convert JS signature to Python if needed
    signature = challenge_data.get("function_signature", f"def {function_name}():")
    if "function " in signature:
        # Basic conversion from JS to Python signature
        signature = signature.replace("function ", "def ").replace(" {", ":").replace("}", "")

    template = f'''"""
Problem: {challenge_data["title"]}

{challenge_data["description"]}
"""
{signature}
    # ✍️ TU CÓDIGO AQUÍ
    pass

# Test Cases (ejecutables)'''

    for i, test_case in enumerate(test_cases):
        template += f'''
print({function_name}({test_case["input"]}))  # Esperado: {test_case["expected"]}'''

    return template

async def analyze_chat_context(chat_context: list, language: str) -> str:
    """Analyze chat context to understand what challenge was discussed"""

    # Convert chat messages to string format
    chat_text = ""
    for message in chat_context:
        role = message.get("role", "unknown")
        content = message.get("content", "")
        chat_text += f"{role}: {content}\n"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": CONTEXT_ANALYSIS_PROMPT.format(chat_context=chat_text)},
                {"role": "user", "content": f"What challenge should I generate for {language} based on this conversation?"}
            ],
            temperature=0.3,
            max_tokens=200
        )

        analysis = response.choices[0].message.content

        return f"Based on the chat conversation, generate a challenge that matches what was discussed: {analysis}"

    except Exception as e:
        # Fallback if analysis fails
        return "Generate an appropriate challenge based on the conversation context provided."