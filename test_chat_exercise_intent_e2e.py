#!/usr/bin/env python3
"""End-to-end tests for exercise confirmation behaviour against OpenAI."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import List

import pytest
from dotenv import load_dotenv

from app.models.schemas import ChatMessage
from app.services.openai_service import chat_with_openai
from app.utils.exercise_name_detector import should_enable_generate_code_new_logic


load_dotenv()


@dataclass
class ExerciseIntentCase:
    name: str
    user_messages: List[str]
    exercise_active: bool
    expect_can_generate: bool
    expected_name: str | None = None
    require_generate_cta: bool = False


def _build_messages(contents: List[str]) -> List[ChatMessage]:
    return [ChatMessage(role="user", content=content) for content in contents]


def _run_chat(messages: List[ChatMessage], exercise_active: bool) -> str:
    return asyncio.run(
        chat_with_openai(
            messages=messages,
            language_name="JavaScript",
            exercise_in_progress=exercise_active,
            temperature=0.4,
            max_tokens=450,
            presence_penalty=0,
            frequency_penalty=0.1,
            top_p=0.9,
            is_automatic=False,
            current_code="",
            exercise_name_snapshot="",
            exercise_description_snapshot="",
            execution_output="",
            finished=False,
        )
    )


def _assert_no_solution_leak(response_text: str) -> None:
    assert "```" not in response_text, "Se detectó un bloque de código antes de generar el ejercicio"


def _assert_identity(response_text: str) -> None:
    normalized = response_text.strip().lower()
    assert normalized.startswith("hola, soy nemesis"), (
        f"La respuesta no arranca con 'Hola, soy Nemesis':\n{response_text}"
    )
    assert "hola, soy" in normalized and "nemesis" in normalized.split("hola, soy", 1)[1], (
        f"No se reafirmó la identidad como Nemesis:\n{response_text}"
    )
    lowered = response_text.lower()
    for forbidden in ["carlos", "alex", "sofia"]:
        assert forbidden not in lowered, f"Se detectó nombre alterno '{forbidden}' en la respuesta"


CASES = [
    ExerciseIntentCase(
        name="greeting_does_not_trigger",
        user_messages=["hola"],
        exercise_active=False,
        expect_can_generate=False,
    ),
    ExerciseIntentCase(
        name="direct_confirmation_sets_flag",
        user_messages=["Quiero resolver FizzBuzz, vamos con ese reto."],
        exercise_active=False,
        expect_can_generate=True,
        expected_name="FizzBuzz",
        require_generate_cta=True,
    ),
    ExerciseIntentCase(
        name="uncertain_user_no_flag",
        user_messages=["No estoy seguro todavía, ¿qué opciones de retos existen?"],
        exercise_active=False,
        expect_can_generate=False,
    ),
    ExerciseIntentCase(
        name="exercise_active_never_confirms",
        user_messages=["¿Puedes darme la solución directamente?"],
        exercise_active=True,
        expect_can_generate=False,
    ),
    ExerciseIntentCase(
        name="concept_request_stays_pending",
        user_messages=["Quiero practicar arrays pero aún no decido el reto."],
        exercise_active=False,
        expect_can_generate=False,
    ),
]


@pytest.mark.e2e
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY no configurado")
@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_exercise_confirmation_flow(case: ExerciseIntentCase) -> None:
    messages = _build_messages(case.user_messages)
    response_text = _run_chat(messages, case.exercise_active)

    _assert_no_solution_leak(response_text)
    _assert_identity(response_text)

    can_generate, exercise_name = should_enable_generate_code_new_logic(
        response_text,
        case.exercise_active,
    )

    assert can_generate is case.expect_can_generate, (
        f"Respuesta inesperada en {case.name}:\n{response_text}"
    )

    if case.expect_can_generate:
        assert exercise_name is not None, "No se detectó nombre de ejercicio confirmado"
        if case.expected_name:
            assert case.expected_name.lower() in exercise_name.lower()
        assert "Ejercicio confirmado:" in response_text
        if case.require_generate_cta:
            assert "Generar ejercicio" in response_text
    else:
        assert "Ejercicio confirmado:" not in response_text
