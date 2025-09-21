from fastapi import APIRouter, HTTPException
from app.models.schemas import ExecuteRequest, ExecuteResponse, LanguagesResponse, Language, DropdownLanguagesResponse, DropdownLanguage
from app.services.judge0_service import execute_code, get_languages, get_supported_languages

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

@router.get("/languages", response_model=LanguagesResponse)
async def get_languages_endpoint():
    """Get all active programming languages from Judge0"""
    try:
        languages_data = await get_languages()
        # Filter only active languages (not archived)
        active_languages = [
            Language(id=lang["id"], name=lang["name"], is_archived=lang.get("is_archived", False))
            for lang in languages_data
            if not lang.get("is_archived", False)
        ]
        return LanguagesResponse(languages=active_languages)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch languages: {str(e)}"
        )

@router.get("/languages/dropdown", response_model=DropdownLanguagesResponse)
async def get_dropdown_languages():
    """Get curated list of languages for dropdown selection"""
    try:
        languages_data = get_supported_languages()
        dropdown_languages = [
            DropdownLanguage(
                id=lang["id"],
                name=lang["name"],
                display_name=lang["display_name"]
            )
            for lang in languages_data
        ]
        return DropdownLanguagesResponse(languages=dropdown_languages)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dropdown languages: {str(e)}"
        )