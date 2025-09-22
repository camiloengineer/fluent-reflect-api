#!/usr/bin/env python3
"""
Script simple para verificar sintaxis y funcionalidad básica
"""

import requests
import json

# Configuración del servidor
BASE_URL = "http://localhost:8000/api"

def test_basic_endpoint():
    """Prueba básica del endpoint"""
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Hola"
            }
        ],
        "language_id": 97,
        "generarCodigo": False,
        "automatic": False
    }

    print("🧪 Probando endpoint básico...")
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_automatic_init():
    """Prueba el prompt automático de inicio"""
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "INIT_INTERVIEW: Preséntate como entrevistador técnico."
            }
        ],
        "language_id": 97,
        "generarCodigo": False,
        "current_code": "",
        "automatic": True
    }

    print("🧪 Probando prompt automático INIT_INTERVIEW...")
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        else:
            result = response.json()
            print(f"Response: {result.get('response', '')[:100]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas...")

    # Verificar que el servidor esté funcionando
    try:
        health = requests.get("http://localhost:8000/health")
        print(f"Health check: {health.status_code}")
    except:
        print("❌ Servidor no responde")
        exit(1)

    # Probar endpoint básico
    if test_basic_endpoint():
        print("✅ Endpoint básico funciona")
    else:
        print("❌ Endpoint básico falló")

    # Probar automatic prompt
    if test_automatic_init():
        print("✅ Prompt automático funciona")
    else:
        print("❌ Prompt automático falló")