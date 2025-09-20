import base64
from typing import Optional

def decode_base64(encoded_str: Optional[str]) -> str:
    """Decode base64 string to UTF-8"""
    if not encoded_str or encoded_str is None:
        return ""
    return base64.b64decode(encoded_str).decode('utf-8')