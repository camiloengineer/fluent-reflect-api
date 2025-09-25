import os
import re
from dataclasses import dataclass

import pytest

from dotenv import load_dotenv

from app.models.schemas import ChatMessage
from app.services.openai_service import chat_with_openai


def _ensure_real_openai_key():
    current = os.getenv("OPENAI_API_KEY", "")
    if current and not current.startswith("__DEV_"):
        return

    load_dotenv(override=True)
    current = os.getenv("OPENAI_API_KEY", "")
    if current and not current.startswith("__DEV_"):
        return

    try:
        with open(".env", "r", encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("OPENAI_API_KEY="):
                    value = line.split("=", 1)[1].strip()
                    if value and not value.startswith("__DEV_"):
                        os.environ["OPENAI_API_KEY"] = value
                        return
    except FileNotFoundError:
        pass


_ensure_real_openai_key()


@dataclass
class VerdictCase:
    name: str
    exercise_name: str
    code: str
    output: str
    expected_pass: bool


VERDICT_CASES = [
    VerdictCase(
        name="sum_ok",
        exercise_name="Suma A+B",
        code="""function sum(a, b) {
  return a + b;
}
""",
        output="sum(2, 3) = 5\n",
        expected_pass=True,
    ),
    VerdictCase(
        name="sum_constant",
        exercise_name="Suma A+B",
        code="""function sum(a, b) {
  return 0;
}
""",
        output="5\n",
        expected_pass=False,
    ),
    VerdictCase(
        name="resta_ok",
        exercise_name="Resta A-B",
        code="""function subtract(a, b) {
  return a - b;
}
""",
        output="-1\n",
        expected_pass=True,
    ),
    VerdictCase(
        name="resta_wrong",
        exercise_name="Resta A-B",
        code="""function subtract(a, b) {
  return a + b;
}
""",
        output="-1\n",
        expected_pass=False,
    ),
    VerdictCase(
        name="array_sum_ok",
        exercise_name="Suma de arreglo",
        code="""function sumArray(numbers) {
  return numbers.reduce((acc, curr) => acc + curr, 0);
}
""",
        output="15\n",
        expected_pass=True,
    ),
    VerdictCase(
        name="array_sum_wrong",
        exercise_name="Suma de arreglo",
        code="""function sumArray(numbers) {
  return numbers.length;
}
""",
        output="15\n",
        expected_pass=False,
    ),
    VerdictCase(
        name="max_ok",
        exercise_name="Mayor del arreglo",
        code="""function getMax(numbers) {
  return Math.max(...numbers);
}
""",
        output="Arreglo: [1, 3, 7, 5]\nMayor: 7\n",
        expected_pass=True,
    ),
    VerdictCase(
        name="max_wrong",
        exercise_name="Mayor del arreglo",
        code="""function getMax(numbers) {
  return numbers[0];
}
""",
        output="7\n",
        expected_pass=False,
    ),
    VerdictCase(
        name="join_ok",
        exercise_name="Unir strings",
        code="""function joinWithDash(items) {
  return items.join('-');
}
""",
        output="a-b-c\n",
        expected_pass=True,
    ),
    VerdictCase(
        name="join_wrong",
        exercise_name="Unir strings",
        code="""function joinWithDash(items) {
  return '';
}
""",
        output="a-b-c\n",
        expected_pass=False,
    ),
]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio("asyncio")
async def test_conversational_tone_end_to_end():
    messages = [ChatMessage(role="user", content="Quiero practicar con arrays hoy." )]

    response = await chat_with_openai(
        messages=messages,
        language_name="JavaScript",
        exercise_in_progress=False,
    )

    lowered = response.lower()
    assert re.match(r"hola[\.,\s]+soy[\s]+nemesis", lowered), response
    assert any(keyword in lowered for keyword in ("arrays", "two sum", "sum")), response
    assert not re.search(r"\b1\.\s", response)


@pytest.mark.anyio("asyncio")
@pytest.mark.parametrize("case", VERDICT_CASES, ids=lambda case: case.name)
async def test_verdict_end_to_end(case: VerdictCase):
    messages = [ChatMessage(role="user", content="Necesito veredicto del ejercicio." )]

    response = await chat_with_openai(
        messages=messages,
        language_name="JavaScript",
        exercise_in_progress=False,
        is_automatic=True,
        current_code=case.code,
        exercise_name=case.exercise_name,
        execution_output=case.output,
        finished=True,
    )

    expected_token = "APROBADO" if case.expected_pass else "REPROBADO"
    rejected_token = "REPROBADO" if case.expected_pass else "APROBADO"

    assert expected_token in response, response
    assert rejected_token not in response, response
    assert response.count("🏆") == 1
