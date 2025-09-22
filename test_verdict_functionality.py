#!/usr/bin/env python3
"""
Script para probar la funcionalidad de veredicto automático
"""

import requests
import json

# Configuración del servidor
BASE_URL = "http://localhost:8000/api"

def test_verdict_approved():
    """Prueba veredicto con ejercicio correctamente completado"""

    # Código correcto para FizzBuzz
    correct_code = """function fizzBuzz(n) {
    for (let i = 1; i <= n; i++) {
        if (i % 15 === 0) {
            console.log("FizzBuzz");
        } else if (i % 3 === 0) {
            console.log("Fizz");
        } else if (i % 5 === 0) {
            console.log("Buzz");
        } else {
            console.log(i);
        }
    }
}

fizzBuzz(15);"""

    # Output correcto de FizzBuzz(15)
    correct_output = """1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": "He terminado mi ejercicio, por favor evalúalo."
            }
        ],
        "languageId": 97,
        "exerciseActive": True,
        "currentCode": correct_code,
        "automatic": True,
        "finished": True,                    # NUEVO: Usuario terminó el ejercicio
        "exerciseName": "FizzBuzz",          # NUEVO: Ejercicio actual
        "executionOutput": correct_output    # NUEVO: Output de la ejecución
    }

    print("🧪 PRUEBA: Veredicto con Ejercicio CORRECTO")
    print("=" * 60)
    print(f"📋 Ejercicio: {payload['exerciseName']}")
    print(f"✅ Finished: {payload['finished']}")
    print(f"🤖 Automatic: {payload['automatic']}")
    print(f"📝 Código: {correct_code[:50]}...")
    print(f"🔍 Output: {correct_output[:50]}...")

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response exitosa:")
            print(f"  canGenerateExercise: {result.get('canGenerateExercise')}")
            print(f"  exerciseName: {result.get('exerciseName')}")
            print(f"\n🏆 VEREDICTO DEL ASISTENTE:")
            print(result.get('response', ''))

            # Verificar si contiene "APROBADO"
            if "APROBADO" in result.get('response', '').upper():
                print(f"\n✅ VEREDICTO DETECTADO: APROBADO")
            elif "REPROBADO" in result.get('response', '').upper():
                print(f"\n❌ VEREDICTO DETECTADO: REPROBADO (¿Error en la lógica?)")
            else:
                print(f"\n⚠️ VEREDICTO NO CLARO")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")

def test_verdict_incorrect():
    """Prueba veredicto con ejercicio incorrectamente completado"""

    # Código incorrecto (no es FizzBuzz real)
    incorrect_code = """function fizzBuzz(n) {
    for (let i = 1; i <= n; i++) {
        console.log("FizzBuzz");  // Siempre imprime FizzBuzz
    }
}

fizzBuzz(5);"""

    # Output incorrecto
    incorrect_output = """FizzBuzz
FizzBuzz
FizzBuzz
FizzBuzz
FizzBuzz"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": "He terminado mi ejercicio, por favor evalúalo."
            }
        ],
        "languageId": 97,
        "exerciseActive": True,
        "currentCode": incorrect_code,
        "automatic": True,
        "finished": True,
        "exerciseName": "FizzBuzz",
        "executionOutput": incorrect_output
    }

    print("\n🧪 PRUEBA: Veredicto con Ejercicio INCORRECTO")
    print("=" * 60)
    print(f"📋 Ejercicio: {payload['exerciseName']}")
    print(f"❌ Código incorrecto: Siempre imprime FizzBuzz")
    print(f"❌ Output incorrecto: Solo FizzBuzz")

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response exitosa:")
            print(f"\n🏆 VEREDICTO DEL ASISTENTE:")
            print(result.get('response', ''))

            # Verificar si contiene "REPROBADO"
            if "REPROBADO" in result.get('response', '').upper():
                print(f"\n✅ VEREDICTO CORRECTO: REPROBADO")
            elif "APROBADO" in result.get('response', '').upper():
                print(f"\n❌ VEREDICTO INCORRECTO: APROBADO (¡Error en la lógica!)")
            else:
                print(f"\n⚠️ VEREDICTO NO CLARO")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")

def test_verdict_manipulated_output():
    """Prueba veredicto con output manipulado"""

    # Código incorrecto
    wrong_code = """function fizzBuzz(n) {
    console.log("Este código no hace FizzBuzz real");
}

fizzBuzz(5);"""

    # Output "correcto" pero que no corresponde al código
    fake_output = """1
2
Fizz
4
Buzz"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": "He terminado mi ejercicio, por favor evalúalo."
            }
        ],
        "languageId": 97,
        "exerciseActive": True,
        "currentCode": wrong_code,
        "automatic": True,
        "finished": True,
        "exerciseName": "FizzBuzz",
        "executionOutput": fake_output
    }

    print("\n🧪 PRUEBA: Veredicto con Output MANIPULADO")
    print("=" * 60)
    print(f"📋 Ejercicio: {payload['exerciseName']}")
    print(f"❌ Código: No hace FizzBuzz")
    print(f"🎭 Output: Parece correcto pero no corresponde al código")

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response exitosa:")
            print(f"\n🏆 VEREDICTO DEL ASISTENTE:")
            print(result.get('response', ''))

            # Verificar si detecta la manipulación
            response_text = result.get('response', '').upper()
            if "REPROBADO" in response_text and ("MANIPUL" in response_text or "INCONSISTEN" in response_text):
                print(f"\n✅ DETECCIÓN CORRECTA: Manipulación detectada")
            elif "REPROBADO" in response_text:
                print(f"\n✅ VEREDICTO CORRECTO: REPROBADO")
            else:
                print(f"\n❌ NO DETECTÓ LA MANIPULACIÓN")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")

def test_validation_finished_requires_automatic():
    """Prueba que finished=True requiere automatic=True"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": "He terminado mi ejercicio."
            }
        ],
        "languageId": 97,
        "exerciseActive": True,
        "currentCode": "function test() {}",
        "automatic": False,              # ❌ Debería ser True cuando finished=True
        "finished": True,
        "exerciseName": "FizzBuzz",
        "executionOutput": "test output"
    }

    print("\n🧪 PRUEBA: Validación finished=True con automatic=False")
    print("=" * 60)
    print(f"❌ Configuración inválida: finished=True pero automatic=False")

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"⚠️ Endpoint aceptó configuración inválida")
            print(f"Response: {result.get('response', '')[:100]}...")
        else:
            print(f"✅ Endpoint rechazó configuración inválida: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 PRUEBAS DE FUNCIONALIDAD DE VEREDICTO")
    print("=" * 70)

    # Verificar health
    try:
        health = requests.get("http://localhost:8000/health")
        print(f"Health check: {health.status_code}")
    except:
        print("❌ Servidor no responde")
        exit(1)

    test_verdict_approved()
    test_verdict_incorrect()
    test_verdict_manipulated_output()
    test_validation_finished_requires_automatic()

    print("\n" + "=" * 70)
    print("✅ PRUEBAS DE VEREDICTO COMPLETADAS")
    print("=" * 70)