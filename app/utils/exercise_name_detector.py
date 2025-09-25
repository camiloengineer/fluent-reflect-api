"""Utility to detect when the assistant locked a concrete exercise."""
import re
from typing import Optional, Tuple


CONFIRMATION_REGEX = re.compile(r"^\s*ejercicio\s+confirmado\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)


def _sanitize_exercise_name(raw_name: str) -> Optional[str]:
    """Trim trailing punctuation and return a clean exercise name."""

    if not raw_name:
        return None

    # Take only the first line in case the assistant adds extra context
    candidate = raw_name.splitlines()[0].strip()

    # Strip trailing punctuation or quotes that may follow the name
    candidate = candidate.rstrip(".?!")
    candidate = candidate.strip("\"'`”’")

    return candidate or None


def detect_concrete_exercise(response_text: str) -> Tuple[bool, Optional[str]]:
    """Detect if the assistant confirmed a concrete exercise via the canonical phrase."""

    if not response_text:
        return False, None

    match = CONFIRMATION_REGEX.search(response_text)
    if not match:
        return False, None

    exercise_name = _sanitize_exercise_name(match.group(1))
    if not exercise_name:
        return False, None

    return True, exercise_name


def should_enable_generate_code_new_logic(
    response_text: str,
    request_exercise_active: bool
) -> Tuple[bool, Optional[str]]:
    """
    New logic for determining can_generate_exercise flag and exercise name.

    LÓGICA:
    - Si exercise_active=True (hay ejercicio activo): NUNCA permitir generar nuevo ejercicio
    - Si exercise_active=False (no hay ejercicio activo): Verificar si se acordó un ejercicio específico

    Args:
        response_text: AI response text
        request_exercise_active: True if exercise is active, False if no active exercise

    Returns:
        Tuple[bool, Optional[str]]: (can_generate_exercise, exercise_name)
    """

    # If request has exercise_active=True, never allow generating new exercise
    # (exercise in progress, don't offer more)
    if request_exercise_active:
        return False, None

    # If request has exercise_active=False, check if we're discussing a concrete exercise
    is_concrete, exercise_name = detect_concrete_exercise(response_text)

    return is_concrete, exercise_name
