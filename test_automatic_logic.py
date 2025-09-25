#!/usr/bin/env python3
"""
Script para verificar la lógica de prompts automáticos sin llamar a OpenAI
"""

from app.services.automatic_prompts_service import (
    detect_automatic_prompt_type,
    get_automatic_system_prompt,
    should_override_exercise_logic
)

def test_detection_logic():
    """Prueba la lógica de detección de prompts automáticos"""

    print("🧪 PROBANDO LÓGICA DE DETECCIÓN DE PROMPTS AUTOMÁTICOS")
    print("=" * 60)

    test_cases = [
        ("INIT_INTERVIEW: Preséntate como entrevistador técnico", "INIT_INTERVIEW"),
        ("HINT_REQUEST: El usuario necesita una pista", "HINT_REQUEST"),
        ("EXERCISE_END: El ejercicio ha terminado", "EXERCISE_END"),
        ("Hola, ¿cómo estás?", None),
        ("¿Puedes ayudarme con arrays?", None),
    ]

    for content, expected in test_cases:
        result = detect_automatic_prompt_type(content)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{content[:50]}...' -> {result} (esperado: {expected})")

def test_system_prompts():
    """Prueba la generación de system prompts"""

    print("\n🧪 PROBANDO GENERACIÓN DE SYSTEM PROMPTS")
    print("=" * 60)

    prompt_types = ["INIT_INTERVIEW", "HINT_REQUEST", "EXERCISE_END", "EXERCISE_VERDICT"]

    for prompt_type in prompt_types:
        prompt = get_automatic_system_prompt(
            prompt_type,
            "JavaScript",
            "console.log('test')",
            exercise_name="FizzBuzz",
            execution_output="1 2 Fizz"
        )
        print(f"\n📝 {prompt_type}:")
        print(f"   Longitud: {len(prompt)} caracteres")
        print(f"   Contiene 'Nemesis': {'✅' if 'Nemesis' in prompt else '❌'}")
        assert "Nemesis" in prompt
        assert "small talk" in prompt.lower()

def test_override_logic():
    """Prueba la lógica de sobrescritura de flags"""

    print("\n🧪 PROBANDO LÓGICA DE SOBRESCRITURA DE FLAGS")
    print("=" * 60)

    expected = (False, None)
    test_cases = ["INIT_INTERVIEW", "HINT_REQUEST", "EXERCISE_END", "EXERCISE_VERDICT"]

    for prompt_type in test_cases:
        result = should_override_exercise_logic(prompt_type)
        status = "✅" if result == expected else "❌"
        print(f"{status} {prompt_type} -> {result} (esperado: {expected})")
        assert result == expected

def test_edge_cases():
    """Prueba casos extremos"""

    print("\n🧪 PROBANDO CASOS EXTREMOS")
    print("=" * 60)

    edge_cases = [
        ("", None),
        ("   ", None),
        ("INIT_INTERVIEW", "INIT_INTERVIEW"),
        ("init_interview: algo", None),  # case sensitive
        ("Esto contiene HINT_REQUEST en el medio", None),  # no debe detectar en el medio
        ("HINT_REQUEST: ", "HINT_REQUEST"),  # con contenido mínimo
    ]

    for content, expected in edge_cases:
        result = detect_automatic_prompt_type(content)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{content}' -> {result} (esperado: {expected})")

if __name__ == "__main__":
    test_detection_logic()
    test_system_prompts()
    test_override_logic()
    test_edge_cases()

    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS DE LÓGICA COMPLETADAS")
    print("=" * 60)
