import base64

def decode_base64(encoded_str: str) -> str:
    """Decode base64 string to UTF-8"""
    if not encoded_str:
        return ""
    return base64.b64decode(encoded_str).decode('utf-8')