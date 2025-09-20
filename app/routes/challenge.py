from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import ChallengeRequest, ChallengeResponse
from app.services.challenge_service import generate_challenge
from app.utils.rate_limiter import check_rate_limit

router = APIRouter()

@router.post("/generate-challenge", response_model=ChallengeResponse)
async def generate_challenge_endpoint(request: ChallengeRequest, client_request: Request):
    """Generate a programming challenge with template code"""
    try:
        # Get client IP for rate limiting
        client_ip = client_request.client.host

        # Apply rate limiting (more restrictive for challenge generation)
        check_rate_limit(client_ip, limit=10, window_seconds=60)

        # Generate challenge
        challenge = await generate_challenge(
            language=request.language,
            difficulty=request.difficulty,
            topic=request.topic,
            chat_context=[msg.dict() for msg in request.chat_context] if request.chat_context else None
        )

        return ChallengeResponse(**challenge)

    except HTTPException:
        # Re-raise HTTP exceptions (like rate limit)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Challenge generation failed: {str(e)}"
        )