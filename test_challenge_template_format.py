from app.services.challenge_service import (
    generate_javascript_template,
    generate_python_template,
)


SAMPLE_CHALLENGE = {
    "title": "Suma A+B",
    "description": "Dado dos enteros a y b, retorna a + b.",
    "function_name": "sum",
    "function_signature": "function sum(a, b)",
    "constraints": [
        "1 ≤ a, b ≤ 10^4",
        "Los parámetros siempre son enteros",
    ],
    "test_cases": [
        {"input": "2, 3", "expected": "5", "explanation": "Caso base"},
        {"input": "4, 7", "expected": "11", "explanation": "Valores positivos"},
    ],
}


def test_javascript_template_includes_metadata_sections():
    template = generate_javascript_template(SAMPLE_CHALLENGE)

    assert "// 🧪 Ejercicio:" in template
    assert "// 📋 Descripción:" in template
    assert "// 📥 Ejemplos de Entrada/Salida:" in template
    assert "// 🛑 Restricciones:" in template
    assert "console.log(sum(2, 3));" in template


def test_python_template_includes_metadata_sections():
    template = generate_python_template(SAMPLE_CHALLENGE)

    assert "# 🧪 Ejercicio:" in template
    assert "# 📋 Descripción:" in template
    assert "# 📥 Ejemplos de Entrada/Salida:" in template
    assert "# 🛑 Restricciones:" in template
    assert "print(sum(2, 3))" in template
