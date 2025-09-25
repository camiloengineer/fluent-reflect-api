from app.services.verdict_chain import build_verdict_reasoning_prompt
import base64


def test_verdict_chain_contains_core_sections():
    description = "Resuelve la suma de dos enteros y retorna el resultado."
    b64_desc = base64.b64encode(description.encode("utf-8")).decode("utf-8")

    prompt = build_verdict_reasoning_prompt(
        language_name="JavaScript",
        exercise_name_snapshot="Suma A+B",
        exercise_description_snapshot=b64_desc,
        current_code="function sum(a, b) { return a + b; }",
        execution_output="5\n",
    )

    expected_chunks = [
        "### PROCESO INTERNO DEL VEREDICTO",
        "1. **Validación de plantilla**",
        "7. **Síntesis final**",
        "#### REGLAS ADICIONALES",
        "#### CASOS AUTOMÁTICOS DE REPROBACIÓN",
        "🏆 **VEREDICTO: [APROBADO/REPROBADO]**",
        "**Decisión Final:**",
    ]

    for chunk in expected_chunks:
        assert chunk in prompt
