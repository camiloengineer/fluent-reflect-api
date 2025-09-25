"""Utility helpers to build the chain-of-thinking prompt for exercise verdicts."""
from __future__ import annotations

import base64
from textwrap import dedent


def build_verdict_reasoning_prompt(
    *,
    language_name: str,
    exercise_name_snapshot: str,
    exercise_description_snapshot: str | None = None,
    current_code: str,
    execution_output: str,
) -> str:
    """Return an additional system prompt enforcing the structured verdict reasoning.

    The prompt encodes a deterministic, step-by-step checklist derived from
    ``chain-of-thinking.txt`` so the LLM must reason before issuing the final
    verdict. We keep it separate from the user-facing output to protect the
    deliberate process.

    TODO: El contexto de mensajes del usuario está eliminado - solo currentCode importa para el veredicto
    TODO: Los snapshots son fuente de verdad prioritaria sobre cualquier contexto conversacional
    """

    # Decodificar descripción base64 para contexto del ejercicio
    decoded_description = None
    if exercise_description_snapshot:
        try:
            decoded_description = base64.b64decode(exercise_description_snapshot).decode('utf-8')
        except Exception:
            decoded_description = None

    exercise_context = decoded_description or exercise_name_snapshot or "el ejercicio solicitado"

    return dedent(
        f"""
        ### PROCESO INTERNO DEL VEREDICTO (NO LO EXPONGAS TAL CUAL)
        Tu respuesta final debe respetar el formato obligatorio del veredicto,
        pero *antes* debes recorrer este razonamiento privado paso a paso.

        1. **Validación de plantilla**: Corrobora que el código enviado para "{exercise_context}" no sea la plantilla vacía, no esté en blanco y compile a nivel sintáctico en {language_name}. Señala si hay comentarios tipo "TODO" o "// TU CÓDIGO AQUÍ".
        2. **Evidencia de compilación**: Examina el output de ejecución. "{execution_output.strip() or '<<output vacío>>'}" debe mostrar señales de haber corrido en consola (logs numéricos, errores, etc.). Si el output está vacío o indica error, el veredicto debe ser REPROBADO.
        3. **Consistencia enunciado-código**: Extrae la intención del ejercicio "{exercise_name_snapshot}" y verifica que la firma, los nombres de funciones y la lógica implementada coincidan con el enunciado.
        4. **Desglose de lógica**: Descompón la implementación en pasos lógicos (mínimo 5 checkpoints conceptuales, incluso si el algoritmo es corto). Evalúa cada checkpoint contra los requisitos.
        5. **Cobertura de casos complejos**: Analiza ramificaciones, bucles y estructura temporal. Si detectas estrategias ineficientes (ej. doble loop para un problema que requiere O(n)), anótalo y marca riesgo de REPROBADO.
        6. **Pruebas mentales**: Ejecuta pruebas rápidas con datos concretos extraídos del enunciado. Ejemplos: sum(2,3) === 5. Ajusta al problema actual. Si la lógica pasa estas pruebas y la salida coincide con los resultados esperados (aunque sea un único valor), considéralo evidencia suficiente.
        7. **Síntesis final**: Decide el veredicto únicamente si todos los pasos anteriores son coherentes. Ante la mínima duda, REPROBADO.

        #### REGLAS ADICIONALES
        - Nunca inventes resultados que el código no puede producir.
        - Si el output fue manipulado o no coincide con la lógica, debes detectarlo y reprobar.
        - Si "finished" es True, asume que el usuario cerró el ejercicio y espera dictamen definitivo en este mismo mensaje.
        - Prioriza precisión sobre indulgencia: dudas ⇒ REPROBADO.
        - No agregues mensajes de espera ni confirmaciones previas; emite el veredicto directamente con el formato indicado.

        #### CASOS AUTOMÁTICOS DE REPROBACIÓN
        - Plantilla o funciones vacías.
        - Código que no compila o tiene syntax errors obvios.
        - Output vacío o sin correlación con el código.
        - Implementación que viola los requisitos declarados.
        - Complejidad claramente incorrecta en ejercicios avanzados (ej. árbol binario con doble loop).

        Este análisis es solo para tu deliberación interna. Después de completarlo,
        genera la respuesta visible siguiendo exactamente el formato:
        🏆 **VEREDICTO: [APROBADO/REPROBADO]**

        **Paso 1 - Implementación:**
        [Resumen sintetizado del paso 1]

        **Paso 2 - Output:**
        [Resumen sintetizado del paso 2]

        **Paso 3 - Coherencia:**
        [Resumen sintetizado del paso 3]

        **Decisión Final:**
        [Razón final, directa y basada en los pasos anteriores]
        """
    ).strip()
