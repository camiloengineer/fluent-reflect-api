#!/usr/bin/env python3
"""
Script para probar análisis detallado del current_code
"""

import requests

BASE_URL = "http://localhost:8000/api"

def test_detailed_analysis():
    """Prueba análisis específico del código con elementos detectables"""

    monaco_code = """function reverseString(str) {
  // ✍️ TU CÓDIGO AQUÍ

}

// Test Cases (ejecutables)
console.log(reverseString('hello')); // Esperado: 'olleh'
console.log(reverseString('programming')); // Esperado: 'gnimmargorp'"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Analiza mi código actual. ¿Qué veo en el editor? ¿Qué necesito implementar?"
            }
        ],
        "language_id": 97,
        "exercise_active": True,
        "current_code": monaco_code,
        "automatic": False
    }

    print("🧪 PRUEBA: Análisis Detallado del Código Actual")
    print("=" * 60)

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)

        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')

            print("📝 RESPUESTA DEL ASISTENTE:")
            print(response_text)

            print("\n🔍 ELEMENTOS ESPECÍFICOS DETECTADOS:")

            # Verificar elementos específicos
            checks = [
                ("función reverseString", "reversestring" in response_text.lower()),
                ("comentario 'TU CÓDIGO AQUÍ'", "tu código aquí" in response_text.lower() or "tu codigo aqui" in response_text.lower()),
                ("test cases", "test" in response_text.lower() and ("console.log" in response_text.lower() or "console" in response_text.lower())),
                ("ejemplo 'hello'", "hello" in response_text.lower()),
                ("resultado esperado 'olleh'", "olleh" in response_text.lower()),
                ("ejemplo 'programming'", "programming" in response_text.lower()),
                ("parámetro 'str'", "str" in response_text.lower() and "parámetro" in response_text.lower()),
            ]

            detected_count = 0
            for description, detected in checks:
                status = "✅" if detected else "❌"
                print(f"  {status} {description}")
                if detected:
                    detected_count += 1

            print(f"\n📊 PUNTUACIÓN: {detected_count}/{len(checks)} elementos detectados")

            if detected_count >= len(checks) * 0.7:  # 70% o más
                print("✅ EXCELENTE: Análisis específico del código")
            elif detected_count >= len(checks) * 0.4:  # 40% o más
                print("⚠️ BUENO: Análisis parcialmente específico")
            else:
                print("❌ MEJORABLE: Análisis genérico")

        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

def test_hint_specific():
    """Prueba hint request con análisis específico"""

    monaco_code = """function reverseString(str) {
  let result = "";
  for (let i = 0; i < str.length; i++) {
    // Aquí estoy intentando algo pero no sé qué hacer
  }
  return result;
}"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": "HINT_REQUEST: Analiza el código actual y da una pista específica."
            }
        ],
        "language_id": 97,
        "exercise_active": True,
        "current_code": monaco_code,
        "automatic": True
    }

    print("\n🧪 PRUEBA: Hint Específico con Loop Implementado")
    print("=" * 60)
    print("📝 CÓDIGO:")
    print(monaco_code)

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)

        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')

            print("\n💡 PISTA DEL ASISTENTE:")
            print(response_text)

            print("\n🔍 ANÁLISIS DE ESPECIFICIDAD:")

            # Verificar elementos específicos del código
            checks = [
                ("variable 'result'", "result" in response_text.lower()),
                ("loop/bucle", "loop" in response_text.lower() or "bucle" in response_text.lower() or "for" in response_text.lower()),
                ("variable 'i'", " i " in response_text.lower() or "'i'" in response_text.lower()),
                ("str.length", "length" in response_text.lower()),
                ("índice hacia atrás", "atrás" in response_text.lower() or "reverso" in response_text.lower() or "final" in response_text.lower()),
            ]

            detected_count = sum(1 for _, detected in checks if detected)

            for description, detected in checks:
                status = "✅" if detected else "❌"
                print(f"  {status} {description}")

            print(f"\n📊 ESPECIFICIDAD: {detected_count}/{len(checks)} elementos específicos")

        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 PRUEBAS DE ANÁLISIS ESPECÍFICO DEL CÓDIGO")
    print("=" * 70)

    try:
        health = requests.get("http://localhost:8000/health")
        print(f"Health check: {health.status_code}")
    except:
        print("❌ Servidor no responde")
        exit(1)

    test_detailed_analysis()
    test_hint_specific()

    print("\n" + "=" * 70)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 70)