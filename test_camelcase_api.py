#!/usr/bin/env python3
"""
Script para probar la transformación camelCase <-> snake_case en la API
"""

import requests
import json

# Configuración del servidor
BASE_URL = "http://localhost:8000/api"

def test_camelcase_request():
    """Prueba enviando request en camelCase desde el frontend"""

    # Request en camelCase (como lo enviaría el frontend)
    camel_payload = {
        "messages": [
            {
                "role": "user",
                "content": "Hola, me gustaría practicar FizzBuzz"
            }
        ],
        "languageId": 97,                    # camelCase
        "exerciseActive": False,             # camelCase
        "currentCode": "// mi código aquí",  # camelCase
        "automatic": False,
        "exerciseName": None,                # camelCase
        "temperature": 0.7,
        "maxTokens": 500,                    # camelCase
        "presencePenalty": 0,                # camelCase
        "frequencyPenalty": 0.3,             # camelCase
        "topP": 0.9                          # camelCase
    }

    print("🧪 PRUEBA: Request con camelCase")
    print("=" * 60)
    print("📤 REQUEST ENVIADO (camelCase):")
    for key, value in camel_payload.items():
        if key == "messages":
            print(f"  {key}: [{len(value)} mensajes]")
        else:
            print(f"  {key}: {value}")

    try:
        response = requests.post(f"{BASE_URL}/chat", json=camel_payload)
        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"\n📥 RESPONSE RECIBIDO:")
            print(f"  response: {result.get('response', '')[:50]}...")

            # Verificar que el response usa camelCase
            camel_keys = ['canGenerateExercise', 'exerciseName']
            snake_keys = ['can_generate_exercise', 'exercise_name']

            print(f"\n🔍 VERIFICACIÓN DE KEYS EN RESPONSE:")
            for camel_key in camel_keys:
                if camel_key in result:
                    print(f"  ✅ {camel_key}: {result[camel_key]}")
                else:
                    print(f"  ❌ {camel_key}: No encontrado")

            for snake_key in snake_keys:
                if snake_key in result:
                    print(f"  ❌ {snake_key}: {result[snake_key]} (¡Debería estar en camelCase!)")
                else:
                    print(f"  ✅ {snake_key}: No presente (correcto)")

            # Verificar funcionalidad específica
            if result.get('canGenerateExercise') and result.get('exerciseName'):
                print(f"  📋 Ejercicio detectado: {result.get('exerciseName')}")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")

def test_snake_case_backward_compatibility():
    """Prueba que el backend aún acepte snake_case para compatibilidad"""

    # Request en snake_case (compatibilidad hacia atrás)
    snake_payload = {
        "messages": [
            {
                "role": "user",
                "content": "Test de compatibilidad snake_case"
            }
        ],
        "language_id": 97,                   # snake_case
        "exercise_active": False,            # snake_case
        "current_code": "// código de prueba", # snake_case
        "automatic": False,
        "exercise_name": None,               # snake_case
    }

    print("\n🧪 PRUEBA: Compatibilidad con snake_case")
    print("=" * 60)
    print("📤 REQUEST ENVIADO (snake_case):")
    for key, value in snake_payload.items():
        if key == "messages":
            print(f"  {key}: [{len(value)} mensajes]")
        else:
            print(f"  {key}: {value}")

    try:
        response = requests.post(f"{BASE_URL}/chat", json=snake_payload)
        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"\n📥 RESPONSE RECIBIDO:")
            print(f"  response: {result.get('response', '')[:50]}...")
            print(f"  ✅ Backend acepta snake_case (compatibilidad)")

            # Verificar que el response sigue siendo camelCase
            if 'canGenerateExercise' in result:
                print(f"  ✅ Response en camelCase: canGenerateExercise")
            else:
                print(f"  ❌ Response no está en camelCase")

        else:
            print(f"⚠️ Error con snake_case: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")

def test_automatic_prompt_camelcase():
    """Prueba prompt automático con camelCase"""

    camel_payload = {
        "messages": [
            {
                "role": "user",
                "content": "INIT_INTERVIEW: Preséntate como entrevistador técnico."
            }
        ],
        "languageId": 97,
        "exerciseActive": False,
        "currentCode": "function test() { return 'hello'; }",
        "automatic": True,
        "exerciseName": None
    }

    print("\n🧪 PRUEBA: Prompt Automático con camelCase")
    print("=" * 60)

    try:
        response = requests.post(f"{BASE_URL}/chat", json=camel_payload)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prompt automático funcionó con camelCase")
            print(f"  canGenerateExercise: {result.get('canGenerateExercise')}")
            print(f"  exerciseName: {result.get('exerciseName')}")

            # Verificar lógica específica de prompts automáticos
            if result.get('canGenerateExercise') == False:
                print(f"  ✅ Lógica correcta: Prompts automáticos no generan ejercicios")
            else:
                print(f"  ❌ Lógica incorrecta en prompt automático")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")

def test_field_transformation():
    """Prueba transformaciones específicas de campos"""

    test_cases = [
        # (frontend_key, backend_expected)
        ("languageId", "language_id"),
        ("exerciseActive", "exercise_active"),
        ("currentCode", "current_code"),
        ("exerciseName", "exercise_name"),
        ("canGenerateExercise", "can_generate_exercise"),
        ("maxTokens", "max_tokens"),
        ("presencePenalty", "presence_penalty"),
        ("frequencyPenalty", "frequency_penalty"),
        ("topP", "top_p")
    ]

    print("\n🔍 VERIFICACIÓN DE TRANSFORMACIONES DE CAMPOS")
    print("=" * 60)

    from app.utils.case_transform import camel_to_snake, snake_to_camel

    for camel_case, expected_snake in test_cases:
        actual_snake = camel_to_snake(camel_case)
        back_to_camel = snake_to_camel(actual_snake)

        snake_ok = actual_snake == expected_snake
        round_trip_ok = back_to_camel == camel_case

        status_snake = "✅" if snake_ok else "❌"
        status_round = "✅" if round_trip_ok else "❌"

        print(f"  {status_snake} {camel_case} -> {actual_snake} (esperado: {expected_snake})")
        print(f"  {status_round} {actual_snake} -> {back_to_camel} (round-trip)")

if __name__ == "__main__":
    print("🚀 PRUEBAS DE TRANSFORMACIÓN CAMELCASE")
    print("=" * 70)

    # Verificar health
    try:
        health = requests.get("http://localhost:8000/health")
        print(f"Health check: {health.status_code}")
    except:
        print("❌ Servidor no responde")
        exit(1)

    test_field_transformation()
    test_camelcase_request()
    test_snake_case_backward_compatibility()
    test_automatic_prompt_camelcase()

    print("\n" + "=" * 70)
    print("✅ PRUEBAS DE CAMELCASE COMPLETADAS")
    print("=" * 70)