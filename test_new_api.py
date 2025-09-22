#!/usr/bin/env python3
"""
Script de prueba para verificar la nueva API con campos en inglés
"""

import requests
import json

# Configuración del servidor
BASE_URL = "http://localhost:8000/api"

def test_automatic_init():
    """Prueba el prompt automático de inicio con nueva API"""
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "INIT_INTERVIEW: Preséntate como entrevistador técnico y sugiere un ejercicio específico."
            }
        ],
        "language_id": 97,
        "exercise_active": False,       # NUEVO CAMPO
        "current_code": "",
        "automatic": True,
        "exercise_name": None           # NUEVO CAMPO
    }

    print("🧪 PRUEBA: INIT_INTERVIEW con nueva API")
    print("=" * 50)
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response exitosa:")
            print(f"  - can_generate_exercise: {result.get('can_generate_exercise')}")
            print(f"  - exercise_name: {result.get('exercise_name')}")
            print(f"  - response: {result.get('response', '')[:100]}...")

            # Verificar lógica correcta
            if result.get('can_generate_exercise') == False and result.get('exercise_name') == None:
                print("✅ Lógica correcta: Prompts automáticos nunca generan ejercicios")
            else:
                print("❌ Lógica incorrecta: Prompts automáticos no deben generar ejercicios")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

def test_normal_chat():
    """Prueba chat normal sin ejercicio activo"""
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Hola, me gustaría practicar FizzBuzz"
            }
        ],
        "language_id": 97,
        "exercise_active": False,       # Sin ejercicio activo
        "automatic": False,             # Chat normal
        "exercise_name": None
    }

    print("\n🧪 PRUEBA: Chat normal mencionando FizzBuzz")
    print("=" * 50)
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response exitosa:")
            print(f"  - can_generate_exercise: {result.get('can_generate_exercise')}")
            print(f"  - exercise_name: {result.get('exercise_name')}")
            print(f"  - response: {result.get('response', '')[:100]}...")

            # Verificar si detectó ejercicio específico
            if result.get('can_generate_exercise') and result.get('exercise_name'):
                print(f"✅ Ejercicio detectado: {result.get('exercise_name')}")
            else:
                print("ℹ️ No se detectó ejercicio específico")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

def test_exercise_active():
    """Prueba con ejercicio activo"""
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "¿Puedes ayudarme con mi código?"
            }
        ],
        "language_id": 97,
        "exercise_active": True,        # Ejercicio activo
        "current_code": "function fizzbuzz() { return 'test'; }",
        "automatic": False,
        "exercise_name": "FizzBuzz"
    }

    print("\n🧪 PRUEBA: Chat con ejercicio activo")
    print("=" * 50)
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response exitosa:")
            print(f"  - can_generate_exercise: {result.get('can_generate_exercise')}")
            print(f"  - exercise_name: {result.get('exercise_name')}")
            print(f"  - response: {result.get('response', '')[:100]}...")

            # Verificar lógica correcta
            if result.get('can_generate_exercise') == False:
                print("✅ Lógica correcta: Con ejercicio activo no se generan nuevos")
            else:
                print("❌ Lógica incorrecta: Con ejercicio activo no debe generar nuevos")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 PRUEBAS DE NUEVA API")
    print("=" * 60)

    # Verificar health
    try:
        health = requests.get("http://localhost:8000/health")
        print(f"Health check: {health.status_code}")
    except:
        print("❌ Servidor no responde")
        exit(1)

    test_automatic_init()
    test_normal_chat()
    test_exercise_active()

    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 60)