#!/usr/bin/env python3
"""
Script para probar la funcionalidad de current_code del editor Monaco
"""

import requests
import json

# Configuración del servidor
BASE_URL = "http://localhost:8000/api"

def test_current_code_context():
    """Prueba que el asistente entienda el current_code del editor Monaco"""

    # Código del ejemplo que me diste
    monaco_code = """function reverseString(str) {
  // ✍️ TU CÓDIGO AQUÍ

}

// Test Cases (ejecutables)
console.log(reverseString('hello')); // Esperado: 'olleh'
console.log(reverseString('programming')); // Esperado: 'gnimmargorp'
console.log(reverseString('12345')); // Esperado: '54321'
console.log(reverseString('racecar')); // Esperado: 'racecar'"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": "¿Puedes ayudarme con mi código? ¿Qué debo hacer?"
            }
        ],
        "language_id": 97,
        "exercise_active": True,           # Hay ejercicio activo
        "current_code": monaco_code,       # Código del editor Monaco
        "automatic": False
    }

    print("🧪 PRUEBA: Current Code Context del Editor Monaco")
    print("=" * 60)
    print(f"📝 CÓDIGO EN EL EDITOR:")
    print(monaco_code[:100] + "...")
    print("\n💬 PREGUNTA DEL USUARIO: '¿Puedes ayudarme con mi código? ¿Qué debo hacer?'")
    print("=" * 60)

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response exitosa:")
            print(f"  - can_generate_exercise: {result.get('can_generate_exercise')}")
            print(f"  - exercise_name: {result.get('exercise_name')}")
            print(f"\n📝 RESPUESTA DEL ASISTENTE:")
            print(f"  {result.get('response', '')}")

            # Verificar si menciona aspectos específicos del código
            response_text = result.get('response', '').lower()
            specific_mentions = []

            if 'reversestring' in response_text or 'reverse string' in response_text:
                specific_mentions.append("✅ Mencionó la función reverseString")
            if 'implementar' in response_text or 'código aquí' in response_text:
                specific_mentions.append("✅ Reconoció que falta implementar")
            if 'test' in response_text or 'console.log' in response_text:
                specific_mentions.append("✅ Reconoció los test cases")
            if 'hello' in response_text or 'olleh' in response_text:
                specific_mentions.append("✅ Mencionó ejemplos específicos")

            print(f"\n🔍 ANÁLISIS DE CONTEXTO:")
            if specific_mentions:
                for mention in specific_mentions:
                    print(f"  {mention}")
            else:
                print("  ❌ No detectó referencias específicas al código actual")

        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

def test_hint_request_with_code():
    """Prueba hint request automático con código actual"""

    monaco_code = """function reverseString(str) {
  let result = "";
  // Intenté hacer algo aquí pero no funciona
  return str;
}"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": "HINT_REQUEST: El usuario necesita una pista sobre el código actual."
            }
        ],
        "language_id": 97,
        "exercise_active": True,
        "current_code": monaco_code,
        "automatic": True
    }

    print("\n🧪 PRUEBA: Hint Request con Current Code")
    print("=" * 60)
    print(f"📝 CÓDIGO EN EL EDITOR:")
    print(monaco_code)
    print("\n🤖 PROMPT AUTOMÁTICO: Solicitud de pista")
    print("=" * 60)

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response exitosa:")
            print(f"\n📝 PISTA DEL ASISTENTE:")
            print(f"  {result.get('response', '')}")

            # Verificar si la pista es específica al código
            response_text = result.get('response', '').lower()
            if 'result' in response_text and 'loop' in response_text:
                print(f"\n✅ Pista específica al código actual")
            else:
                print(f"\n⚠️ Pista genérica, podría ser más específica")

        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

def test_empty_current_code():
    """Prueba comportamiento sin current_code"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": "¿Cómo puedo implementar una función que invierta una cadena?"
            }
        ],
        "language_id": 97,
        "exercise_active": False,
        "current_code": "",               # Sin código actual
        "automatic": False
    }

    print("\n🧪 PRUEBA: Sin Current Code")
    print("=" * 60)
    print("💬 PREGUNTA: '¿Cómo puedo implementar una función que invierta una cadena?'")
    print("📝 SIN CÓDIGO EN EL EDITOR")
    print("=" * 60)

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response exitosa:")
            print(f"  - can_generate_exercise: {result.get('can_generate_exercise')}")
            print(f"  - exercise_name: {result.get('exercise_name')}")
            print(f"\n📝 RESPUESTA DEL ASISTENTE:")
            print(f"  {result.get('response', '')[:200]}...")

        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 PRUEBAS DE CURRENT_CODE DEL EDITOR MONACO")
    print("=" * 70)

    # Verificar health
    try:
        health = requests.get("http://localhost:8000/health")
        print(f"Health check: {health.status_code}")
    except:
        print("❌ Servidor no responde")
        exit(1)

    test_current_code_context()
    test_hint_request_with_code()
    test_empty_current_code()

    print("\n" + "=" * 70)
    print("✅ PRUEBAS DE CURRENT_CODE COMPLETADAS")
    print("=" * 70)