from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import ChatRequest, ChatResponse
from app.services.openai_service import chat_with_openai
from app.services.judge0_service import get_language_name
from app.utils.message_utils import trim_messages
from app.utils.rate_limiter import check_rate_limit, cleanup_old_ips
from app.utils.exercise_name_detector import should_enable_generate_code_new_logic
import random

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, client_request: Request):
    """Chat endpoint using OpenAI GPT with FluentReflect system prompt"""
    try:
        # Get client IP for rate limiting
        client_ip = client_request.client.host

        # Apply rate limiting
        check_rate_limit(client_ip)

        # Periodically cleanup old IPs (10% chance per request)
        if random.random() < 0.1:
            cleanup_old_ips()

        # Apply sliding window: keep only last 7 messages (+ system messages)
        trimmed_messages = trim_messages(request.messages, limit=7)

        # Get language name from language_id
        language_name = get_language_name(request.language_id)

        # Handle automatic prompts with special logic
        if request.automatic:
            from app.services.automatic_prompts_service import detect_automatic_prompt_type, should_override_exercise_logic

            # Get the user message content to detect prompt type
            user_message_content = ""
            if request.messages and request.messages[-1].role == "user":
                user_message_content = request.messages[-1].content

            prompt_type = detect_automatic_prompt_type(user_message_content, request.finished)

            # Call OpenAI with automatic prompt handling
            response = await chat_with_openai(
                messages=trimmed_messages,
                language_name=language_name,
                exercise_in_progress=request.exercise_active,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                presence_penalty=request.presence_penalty,
                frequency_penalty=request.frequency_penalty,
                top_p=request.top_p,
                is_automatic=True,
                current_code=request.current_code or "",
                exercise_name=request.exercise_name or "",
                execution_output=request.execution_output or "",
                finished=request.finished
            )

            # Use automatic prompt logic for response flags
            if prompt_type:
                can_generate_exercise, exercise_name = should_override_exercise_logic(prompt_type)
            else:
                # Fallback to normal logic if prompt type not recognized
                can_generate_exercise, exercise_name = should_enable_generate_code_new_logic(
                    response, request.exercise_active
                )
        else:
            # Normal chat processing
            response = await chat_with_openai(
                messages=trimmed_messages,
                language_name=language_name,
                exercise_in_progress=request.exercise_active,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                presence_penalty=request.presence_penalty,
                frequency_penalty=request.frequency_penalty,
                top_p=request.top_p,
                is_automatic=False,
                current_code=request.current_code or "",
                exercise_name=request.exercise_name or "",
                execution_output=request.execution_output or "",
                finished=request.finished
            )

            # Use normal logic to determine response flags
            can_generate_exercise, exercise_name = should_enable_generate_code_new_logic(
                response, request.exercise_active
            )

        return ChatResponse(
            response=response,
            can_generate_exercise=can_generate_exercise,
            exercise_name=exercise_name
        )

    except HTTPException:
        # Re-raise HTTP exceptions (like rate limit)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )