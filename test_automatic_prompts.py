#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de prompts automáticos
"""

import requests
import json

# Configuración del servidor
BASE_URL = "http://localhost:8000/api"

def run_automatic_prompt(prompt_type: str, content: str, current_code: str = "", generar_codigo: bool = False):
    """Prueba un tipo específico de prompt automático"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "language_id": 97,  # JavaScript
        "generarCodigo": generar_codigo,
        "current_code": current_code,
        "automatic": True,
        "temperature": 0.7,
        "max_tokens": 500
    }

    print(f"\n{'='*60}")
    print(f"🧪 PRUEBA: {prompt_type}")
    print(f"{'='*60}")
    print(f"📤 REQUEST:")
    print(f"  - content: {content}")
    print(f"  - current_code: {current_code[:50] + '...' if len(current_code) > 50 else current_code}")
    print(f"  - generar_codigo: {generar_codigo}")
    print(f"  - automatic: True")

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()

        result = response.json()

        print(f"\n📥 RESPONSE:")
        print(f"  - Status: {response.status_code}")
        print(f"  - generarCodigo: {result.get('generarCodigo')}")
        print(f"  - nombreEjercicio: {result.get('nombreEjercicio')}")
        print(f"\n📝 CONTENIDO DE RESPUESTA:")
        print(f"  {result.get('response', 'No response')}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        return None

def main():
    """Ejecuta todas las pruebas de prompts automáticos"""

    print("🚀 INICIANDO PRUEBAS DE PROMPTS AUTOMÁTICOS")
    print("=" * 60)

    # Prueba 1: Inicio de entrevista
    run_automatic_prompt(
        "INIT_INTERVIEW",
        "INIT_INTERVIEW: Preséntate como entrevistador técnico y ofrece desafíos de programación disponibles en este lenguaje.",
        "",
        False
    )

    # Prueba 2: Solicitud de pista
    run_automatic_prompt(
        "HINT_REQUEST",
        "HINT_REQUEST: El usuario necesita una pista sobre el código actual. Analiza el código y da una pista específica pero no la solución completa.",
        """function findMax(arr) {
    // código incompleto del usuario
    let max = 0;
    return max;
}""",
        True
    )

    # Prueba 3: Finalización de ejercicio
    run_automatic_prompt(
        "EXERCISE_END",
        "EXERCISE_END: El ejercicio ha terminado (tiempo agotado o usuario se rindió). Proporciona feedback sobre lo que faltó, da las gracias y menciona que solo es posible generar un nuevo desafío.",
        """function findMax(arr) {
    let max = 0;
    // código incompleto...
}""",
        True
    )

    print(f"\n{'='*60}")
    print("✅ PRUEBAS COMPLETADAS")
    print("="*60)

if __name__ == "__main__":
    main()
