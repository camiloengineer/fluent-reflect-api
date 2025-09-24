import os
from typing import Optional

try:
    import firebase_admin  # type: ignore
    from firebase_admin import auth, credentials  # type: ignore
    _FIREBASE_AVAILABLE = True
except ImportError:  # pragma: no cover
    firebase_admin = None  # type: ignore
    auth = None  # type: ignore
    credentials = None  # type: ignore
    _FIREBASE_AVAILABLE = False
from fastapi import HTTPException, status

_initialized = False

def _init_if_needed():
    global _initialized
    if _initialized:
        return
    # Uses default application credentials (ADC) - in Cloud Run set GOOGLE_APPLICATION_CREDENTIALS or
    # mount secret JSON. If not present, will try metadata service credentials (not sufficient for Firebase).
    cred_path = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if cred_path and os.path.isfile(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback to initialize without explicit cert (will work only for limited operations if service account has perms)
        firebase_admin.initialize_app()
    _initialized = True

def verify_bearer_token(id_token: str) -> dict:
    if not _FIREBASE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="firebase_admin not installed on server. Install firebase-admin and redeploy.",
        )
    _init_if_needed()
    try:
        decoded = auth.verify_id_token(id_token, clock_skew_seconds=30)
        return decoded
    except Exception as exc:  # broad catch to avoid leaking internal errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase ID token",
        ) from exc

def get_uid(id_token: str) -> Optional[str]:
    data = verify_bearer_token(id_token)
    return data.get("uid")
