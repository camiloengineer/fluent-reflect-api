"""Snapshot validation utilities for exercise consistency checking."""

import base64
from typing import Optional, Tuple


def validate_exercise_snapshots(
    exercise_name_snapshot: Optional[str],
    exercise_description_snapshot: Optional[str]
) -> Tuple[bool, str]:
    """
    Validate snapshot consistency for exercise requests.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """

    # Case 1: No exercise active
    if not exercise_name_snapshot and not exercise_description_snapshot:
        return True, ""

    # Case 2: Inconsistent snapshots (security error)
    if exercise_name_snapshot and not exercise_description_snapshot:
        return False, "Security error: exercise name without description snapshot"

    if not exercise_name_snapshot and exercise_description_snapshot:
        return False, "Security error: exercise description without name snapshot"

    # Case 3: Both present - validate base64 format
    if exercise_description_snapshot:
        try:
            base64.b64decode(exercise_description_snapshot).decode('utf-8')
        except Exception:
            return False, "Invalid base64 format in exercise description snapshot"

    return True, ""


def decode_exercise_description_snapshot(
    exercise_description_snapshot: Optional[str]
) -> Optional[str]:
    """
    Safely decode base64 exercise description snapshot.

    Returns:
        Decoded description string or None if invalid/empty
    """
    if not exercise_description_snapshot:
        return None

    try:
        return base64.b64decode(exercise_description_snapshot).decode('utf-8')
    except Exception:
        return None


def encode_exercise_description_for_response(description: str) -> str:
    """
    Encode exercise description to base64 for frontend response.

    Args:
        description: Plain text description

    Returns:
        Base64 encoded description
    """
    return base64.b64encode(description.encode('utf-8')).decode('ascii')