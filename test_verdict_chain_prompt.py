from app.services.verdict_chain import build_verdict_reasoning_prompt


def test_verdict_chain_contains_core_sections():
    prompt = build_verdict_reasoning_prompt(
        language_name="JavaScript",
        exercise_name="Suma A+B",
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
