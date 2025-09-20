from fastapi import APIRouter, HTTPException
from app.models.schemas import ExecuteRequest, ExecuteResponse
from app.services.judge0_service import execute_code

router = APIRouter()

@router.post("/execute", response_model=ExecuteResponse)
async def execute_code_endpoint(request: ExecuteRequest):
    """Execute code endpoint - replicates frontend handleRunCode logic"""
    try:
        result = await execute_code(
            language_id=request.language_id,
            source_code=request.source_code,
            stdin=request.stdin
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Execution failed: {str(e)}"
        )