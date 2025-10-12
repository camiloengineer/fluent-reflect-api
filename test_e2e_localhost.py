#!/usr/bin/env python3
"""Test E2E against localhost using curl commands"""

import requests
import json
import time

LOCALHOST_URL = "http://localhost:8001/api/chat"
PRODUCTION_URL = "https://fluent-reflect-api-581268440769.us-central1.run.app/api/chat"

def test_fizzbuzz_request():
    """Test FizzBuzz request that should trigger exercise confirmation"""
    payload = {
        "messages": [
            {"role": "user", "content": "Quiero resolver FizzBuzz, vamos con ese reto."}
        ],
        "languageId": 97,
        "exerciseActive": False,
        "currentCode": "",
        "automatic": False,
        "finished": False,
        "executionOutput": "",
        "temperature": 0.4,
        "maxTokens": 450,
        "presencePenalty": 0,
        "frequencyPenalty": 0.1,
        "topP": 0.9
    }
    return payload

def test_greeting_request():
    """Test simple greeting that should not trigger exercise confirmation"""
    payload = {
        "messages": [
            {"role": "user", "content": "hola"}
        ],
        "languageId": 97,
        "exerciseActive": False,
        "currentCode": "",
        "automatic": False,
        "finished": False,
        "executionOutput": "",
        "temperature": 0.4,
        "maxTokens": 450,
        "presencePenalty": 0,
        "frequencyPenalty": 0.1,
        "topP": 0.9
    }
    return payload

def send_request(url, payload):
    """Send request and return response"""
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def analyze_response(response_data, test_name):
    """Analyze response and extract key information"""
    if "error" in response_data:
        return {
            "test": test_name,
            "error": response_data["error"],
            "valid": False
        }

    response_text = response_data.get("response", "")
    can_generate = response_data.get("canGenerateExercise", False)
    exercise_name = response_data.get("exerciseName")

    # Check identity
    starts_with_nemesis = response_text.lower().strip().startswith("hola, soy nemesis")

    # Check forbidden names
    forbidden_names = ["carlos", "alex", "sofia"]
    contains_forbidden = any(name in response_text.lower() for name in forbidden_names)

    # Check for code blocks (solution leak)
    has_code_blocks = "```" in response_text

    # Check for confirmation phrase
    has_confirmation = "Ejercicio confirmado:" in response_text

    return {
        "test": test_name,
        "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text,
        "can_generate_exercise": can_generate,
        "exercise_name": exercise_name,
        "starts_with_nemesis": starts_with_nemesis,
        "contains_forbidden_names": contains_forbidden,
        "forbidden_names_found": [name for name in forbidden_names if name in response_text.lower()],
        "has_code_blocks": has_code_blocks,
        "has_confirmation": has_confirmation,
        "valid": True
    }

def run_tests():
    """Run all tests against both localhost and production"""

    print("=== Testing localhost (http://localhost:8001) ===\n")

    # Wait for server to be ready
    time.sleep(2)

    # Test 1: FizzBuzz confirmation
    print("Test 1: FizzBuzz Confirmation Request")
    fizzbuzz_payload = test_fizzbuzz_request()
    localhost_fizzbuzz = send_request(LOCALHOST_URL, fizzbuzz_payload)
    result1_local = analyze_response(localhost_fizzbuzz, "fizzbuzz_localhost")
    print(f"Result: {json.dumps(result1_local, indent=2, ensure_ascii=False)}\n")

    # Test 2: Greeting
    print("Test 2: Simple Greeting Request")
    greeting_payload = test_greeting_request()
    localhost_greeting = send_request(LOCALHOST_URL, greeting_payload)
    result2_local = analyze_response(localhost_greeting, "greeting_localhost")
    print(f"Result: {json.dumps(result2_local, indent=2, ensure_ascii=False)}\n")

    print("=== Testing production ===\n")

    # Test 1: FizzBuzz confirmation (production)
    print("Test 1: FizzBuzz Confirmation Request (Production)")
    production_fizzbuzz = send_request(PRODUCTION_URL, fizzbuzz_payload)
    result1_prod = analyze_response(production_fizzbuzz, "fizzbuzz_production")
    print(f"Result: {json.dumps(result1_prod, indent=2, ensure_ascii=False)}\n")

    # Test 2: Greeting (production)
    print("Test 2: Simple Greeting Request (Production)")
    production_greeting = send_request(PRODUCTION_URL, greeting_payload)
    result2_prod = analyze_response(production_greeting, "greeting_production")
    print(f"Result: {json.dumps(result2_prod, indent=2, ensure_ascii=False)}\n")

    print("=== COMPARISON SUMMARY ===\n")

    # Compare FizzBuzz results
    print("FizzBuzz Request Comparison:")
    print(f"  Localhost can_generate_exercise: {result1_local.get('can_generate_exercise', 'ERROR')}")
    print(f"  Production can_generate_exercise: {result1_prod.get('can_generate_exercise', 'ERROR')}")
    print(f"  Localhost starts_with_nemesis: {result1_local.get('starts_with_nemesis', 'ERROR')}")
    print(f"  Production starts_with_nemesis: {result1_prod.get('starts_with_nemesis', 'ERROR')}")
    print(f"  Localhost forbidden_names: {result1_local.get('forbidden_names_found', 'ERROR')}")
    print(f"  Production forbidden_names: {result1_prod.get('forbidden_names_found', 'ERROR')}")
    print(f"  Localhost has_confirmation: {result1_local.get('has_confirmation', 'ERROR')}")
    print(f"  Production has_confirmation: {result1_prod.get('has_confirmation', 'ERROR')}")
    print()

    # Compare Greeting results
    print("Greeting Request Comparison:")
    print(f"  Localhost can_generate_exercise: {result2_local.get('can_generate_exercise', 'ERROR')}")
    print(f"  Production can_generate_exercise: {result2_prod.get('can_generate_exercise', 'ERROR')}")
    print(f"  Localhost starts_with_nemesis: {result2_local.get('starts_with_nemesis', 'ERROR')}")
    print(f"  Production starts_with_nemesis: {result2_prod.get('starts_with_nemesis', 'ERROR')}")
    print(f"  Localhost forbidden_names: {result2_local.get('forbidden_names_found', 'ERROR')}")
    print(f"  Production forbidden_names: {result2_prod.get('forbidden_names_found', 'ERROR')}")
    print()

if __name__ == "__main__":
    run_tests()