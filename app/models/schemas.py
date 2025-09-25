from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class CamelCaseModel(BaseModel):
    """
    Base model that handles camelCase aliases for all fields
    """
    model_config = ConfigDict(
        alias_generator=None,  # We'll use explicit aliases
        populate_by_name=True,  # Allow both field name and alias
        by_alias=True  # Use aliases for serialization
    )

class ExecuteRequest(CamelCaseModel):
    language_id: int = Field(alias="languageId")
    source_code: str = Field(alias="sourceCode")
    stdin: Optional[str] = Field(default="", alias="stdin")

class ExecuteResponse(CamelCaseModel):
    status: Optional[str] = Field(alias="status")
    stdout: Optional[str] = Field(alias="stdout")
    stderr: Optional[str] = Field(alias="stderr")
    compile_output: Optional[str] = Field(alias="compileOutput")
    time: Optional[str] = Field(alias="time")
    memory: Optional[int] = Field(alias="memory")
    exit_code: Optional[int] = Field(alias="exitCode")

class ChatMessage(CamelCaseModel):
    role: str = Field(alias="role")  # "system", "user", "assistant"
    content: str = Field(alias="content")

class ChatRequest(CamelCaseModel):
    messages: Optional[List[ChatMessage]] = Field(default=None, alias="messages")  # Can be null for verdict requests
    language_id: int = Field(default=97, alias="languageId")  # Always sent, default JavaScript
    exercise_active: bool = Field(default=False, alias="exerciseActive")  # Always sent
    current_code: str = Field(default="", alias="currentCode")  # Always sent, empty string if no code
    automatic: bool = Field(default=False, alias="automatic")  # Always sent
    exercise_name_snapshot: Optional[str] = Field(default=None, alias="exerciseNameSnapshot")  # Always sent, snapshot prioritario
    exercise_description_snapshot: Optional[str] = Field(default=None, alias="exerciseDescriptionSnapshot")  # Always sent, snapshot en base64
    finished: bool = Field(default=False, alias="finished")  # Always sent
    execution_output: str = Field(default="", alias="executionOutput")  # Always sent, empty if no output

class ChatResponse(CamelCaseModel):
    response: str = Field(alias="response")  # Always sent
    can_generate_exercise: bool = Field(default=False, alias="canGenerateExercise")  # Always sent
    exercise_name: Optional[str] = Field(default=None, alias="exerciseName")  # Always sent, null if no exercise agreed
    exercise_description: Optional[str] = Field(default=None, alias="exerciseDescription")  # Always sent, base64 encoded description

class ChallengeRequest(CamelCaseModel):
    language: str = Field(default="javascript", alias="language")
    difficulty: Optional[str] = Field(default="easy", alias="difficulty")  # easy, medium, hard
    topic: Optional[str] = Field(default=None, alias="topic")  # arrays, algorithms, strings, etc.
    exercise_name: Optional[str] = Field(default=None, alias="exerciseName")  # Specific exercise name agreed upon in chat
    chat_context: Optional[List[ChatMessage]] = Field(default=None, alias="chatContext")  # Context from chat conversation

class ChallengeResponse(CamelCaseModel):
    challenge_id: str = Field(alias="challengeId")
    title: str = Field(alias="title")
    description: str = Field(alias="description")
    template_code: str = Field(alias="templateCode")
    exercise_description: str = Field(alias="exerciseDescription")

class Language(CamelCaseModel):
    id: int = Field(alias="id")
    name: str = Field(alias="name")
    is_archived: bool = Field(alias="isArchived")

class LanguagesResponse(CamelCaseModel):
    languages: List[Language] = Field(alias="languages")

class DropdownLanguage(CamelCaseModel):
    id: int = Field(alias="id")
    name: str = Field(alias="name")
    display_name: str = Field(alias="displayName")  # For dropdown display (e.g., "JavaScript (Node.js 20 LTS)")

class DropdownLanguagesResponse(CamelCaseModel):
    languages: List[DropdownLanguage] = Field(alias="languages")
