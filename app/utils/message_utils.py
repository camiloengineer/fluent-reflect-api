from typing import List
from app.models.schemas import ChatMessage

def trim_messages(messages: List[ChatMessage], limit: int = 7) -> List[ChatMessage]:
    """
    Keep only the last N messages, but always preserve system messages.

    Args:
        messages: List of chat messages
        limit: Maximum number of non-system messages to keep

    Returns:
        Trimmed list with system messages + last N other messages
    """
    if not messages:
        return messages

    # Separate system messages from others
    system_messages = [msg for msg in messages if msg.role == "system"]
    other_messages = [msg for msg in messages if msg.role != "system"]

    # Keep only the last N non-system messages
    trimmed_other = other_messages[-limit:] if len(other_messages) > limit else other_messages

    # Return system messages first, then trimmed others
    return system_messages + trimmed_other