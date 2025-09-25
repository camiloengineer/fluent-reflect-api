#!/usr/bin/env python3
"""
Test script para medir tiempos y tokens de diferentes reasoning efforts en GPT-5-mini.
Compara minimal, low, medium, high con el mismo input complejo de programación.
"""

import os
import requests
import json
import time
import statistics
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_reasoning_effort(effort_level: str, input_text: str, max_tokens: int = 400) -> Dict:
    """Test a specific reasoning effort level and measure performance."""

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    payload = {
        'model': 'gpt-5-mini',
        'input': input_text,
        'max_output_tokens': max_tokens,
        'truncation': 'auto',
        'reasoning': {'effort': effort_level}
    }

    start_time = time.time()

    try:
        response = requests.post(
            'https://api.openai.com/v1/responses',
            headers=headers,
            data=json.dumps(payload),
            timeout=120
        )

        end_time = time.time()
        response_time = end_time - start_time

        response.raise_for_status()
        data = response.json()

        # Extract response text
        texts = []
        for item in data.get('output', []):
            if item.get('type') == 'message':
                for part in item.get('content', []):
                    if part.get('type') == 'output_text':
                        texts.append(part.get('text', ''))

        result_text = '\n'.join(texts)

        # Get usage stats
        usage = data.get('usage', {})

        return {
            'effort': effort_level,
            'status': data.get('status', 'unknown'),
            'response_time_seconds': round(response_time, 3),
            'input_tokens': usage.get('input_tokens', 0),
            'output_tokens': usage.get('output_tokens', 0),
            'reasoning_tokens': usage.get('output_tokens_details', {}).get('reasoning_tokens', 0),
            'total_tokens': usage.get('total_tokens', 0),
            'response_length_chars': len(result_text),
            'response_empty': len(result_text.strip()) == 0,
            'incomplete': data.get('status') == 'incomplete',
            'incomplete_reason': data.get('incomplete_details', {}).get('reason', None),
            'request_id': response.headers.get('x-request-id', 'unknown'),
            'response_preview': result_text[:100] + '...' if len(result_text) > 100 else result_text
        }

    except requests.exceptions.RequestException as e:
        end_time = time.time()
        return {
            'effort': effort_level,
            'status': 'error',
            'response_time_seconds': round(end_time - start_time, 3),
            'error': str(e),
            'input_tokens': 0,
            'output_tokens': 0,
            'reasoning_tokens': 0,
            'total_tokens': 0,
            'response_length_chars': 0,
            'response_empty': True,
            'incomplete': True,
            'incomplete_reason': 'request_error',
            'request_id': 'error',
            'response_preview': f'ERROR: {str(e)}'
        }

def run_reasoning_benchmark():
    """Run benchmark tests for all reasoning effort levels."""

    # Test input: Problema complejo de programación que requiere razonamiento
    test_input = """SYSTEM: Eres Nemesis, un entrevistador técnico experto.

USER: Necesito ayuda con este problema complejo de algorítmica:

"Implementa una función que encuentre el camino más corto en una matriz de NxM donde cada celda tiene un costo de movimiento diferente. Puedes moverte en 4 direcciones (arriba, abajo, izquierda, derecha) pero no en diagonales. El algoritmo debe ser eficiente para matrices grandes.

Explica tu enfoque, implementa la solución paso a paso, analiza la complejidad temporal y espacial, y proporciona ejemplos de prueba."

Proporciona una explicación detallada y el código completo optimizado."""

    efforts = ['minimal', 'low', 'medium', 'high']
    results = []

    print("🧪 BENCHMARK: Comparando Reasoning Efforts de GPT-5-mini")
    print("=" * 80)
    print(f"Input length: {len(test_input)} chars")
    print(f"Max output tokens: 600")
    print("-" * 80)

    for effort in efforts:
        print(f"\n🔄 Testing effort: {effort.upper()}")
        print("-" * 40)

        try:
            result = test_reasoning_effort(effort, test_input, max_tokens=600)
            results.append(result)

            # Display immediate results
            status_emoji = "✅" if result['status'] == 'completed' else "⚠️" if result['status'] == 'incomplete' else "❌"
            print(f"{status_emoji} Status: {result['status']}")
            print(f"⏱️  Time: {result['response_time_seconds']}s")
            print(f"🔤 Response chars: {result['response_length_chars']}")
            print(f"🟦 Input tokens: {result['input_tokens']}")
            print(f"🟩 Output tokens: {result['output_tokens']}")
            print(f"🟨 Reasoning tokens: {result['reasoning_tokens']}")
            print(f"🔢 Total tokens: {result['total_tokens']}")

            if result['incomplete']:
                print(f"⚠️  Incomplete reason: {result['incomplete_reason']}")

            if result['response_empty']:
                print("⚠️  WARNING: Empty response!")
            else:
                print(f"📝 Preview: {result['response_preview']}")

            print(f"🔍 Request ID: {result['request_id']}")

        except Exception as e:
            print(f"❌ Error testing {effort}: {e}")
            results.append({
                'effort': effort,
                'status': 'error',
                'error': str(e),
                'response_time_seconds': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'reasoning_tokens': 0,
                'total_tokens': 0,
                'response_length_chars': 0,
                'response_empty': True
            })

    # Summary analysis
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 80)

    # Table header
    print(f"{'Effort':<10} {'Time(s)':<8} {'Status':<12} {'Out/Rsn Tokens':<15} {'Chars':<6} {'Empty':<6}")
    print("-" * 80)

    # Table rows
    successful_results = []
    for r in results:
        if r['status'] != 'error':
            successful_results.append(r)

        empty_indicator = "YES" if r['response_empty'] else "NO"
        tokens_ratio = f"{r['output_tokens']}/{r['reasoning_tokens']}"

        print(f"{r['effort']:<10} {r['response_time_seconds']:<8} {r['status']:<12} {tokens_ratio:<15} {r['response_length_chars']:<6} {empty_indicator:<6}")

    if successful_results:
        print("\n📈 ESTADÍSTICAS:")
        times = [r['response_time_seconds'] for r in successful_results]
        reasoning_tokens = [r['reasoning_tokens'] for r in successful_results]
        output_tokens = [r['output_tokens'] for r in successful_results]

        print(f"⏱️  Tiempo promedio: {statistics.mean(times):.2f}s")
        print(f"⏱️  Tiempo más rápido: {min(times):.2f}s ({[r['effort'] for r in successful_results if r['response_time_seconds'] == min(times)][0]})")
        print(f"⏱️  Tiempo más lento: {max(times):.2f}s ({[r['effort'] for r in successful_results if r['response_time_seconds'] == max(times)][0]})")

        print(f"🟨 Reasoning tokens promedio: {statistics.mean(reasoning_tokens):.0f}")
        print(f"🟩 Output tokens promedio: {statistics.mean(output_tokens):.0f}")

        # Efficiency analysis
        non_empty = [r for r in successful_results if not r['response_empty']]
        if non_empty:
            print(f"\n💡 RECOMENDACIONES:")
            best_effort = max(non_empty, key=lambda x: x['response_length_chars'] / max(x['response_time_seconds'], 0.1))
            print(f"🏆 Mejor relación contenido/tiempo: {best_effort['effort']} ({best_effort['response_length_chars']} chars en {best_effort['response_time_seconds']}s)")

            fastest_with_content = min(non_empty, key=lambda x: x['response_time_seconds'])
            print(f"🚀 Más rápido con contenido: {fastest_with_content['effort']} ({fastest_with_content['response_time_seconds']}s)")

    # Save results to JSON for further analysis
    output_file = 'reasoning_benchmark_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'test_input': test_input,
            'test_timestamp': time.time(),
            'results': results
        }, f, indent=2)

    print(f"\n💾 Resultados guardados en: {output_file}")
    return results

if __name__ == "__main__":
    try:
        results = run_reasoning_benchmark()
        print("\n✅ Benchmark completado exitosamente")
    except Exception as e:
        print(f"\n❌ Error en benchmark: {e}")