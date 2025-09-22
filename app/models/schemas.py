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
    messages: List[ChatMessage] = Field(alias="messages")
    language_id: Optional[int] = Field(default=97, alias="languageId")  # Default to JavaScript (Node.js 20 LTS)
    exercise_active: Optional[bool] = Field(default=False, alias="exerciseActive")  # true: exercise in progress, false: no active exercise
    current_code: Optional[str] = Field(default="", alias="currentCode")  # Current code being worked on for context
    automatic: Optional[bool] = Field(default=False, alias="automatic")  # true: automatic prompt from frontend, false: normal user message
    exercise_name: Optional[str] = Field(default=None, alias="exerciseName")  # Name of specific exercise to work on (for challenge generation)
    finished: Optional[bool] = Field(default=False, alias="finished")  # true: user finished exercise, requesting verdict (ALWAYS automatic=true)
    execution_output: Optional[str] = Field(default="", alias="executionOutput")  # Output from console.log/print (for verdict evaluation)
    temperature: Optional[float] = Field(default=0.5, alias="temperature")
    max_tokens: Optional[int] = Field(default=400, alias="maxTokens")
    presence_penalty: Optional[float] = Field(default=0, alias="presencePenalty")
    frequency_penalty: Optional[float] = Field(default=0.2, alias="frequencyPenalty")
    top_p: Optional[float] = Field(default=0.9, alias="topP")

class ChatResponse(CamelCaseModel):
    response: str = Field(alias="response")
    can_generate_exercise: bool = Field(default=False, alias="canGenerateExercise")  # true: specific exercise agreed upon, ready to generate code challenge
    exercise_name: Optional[str] = Field(default=None, alias="exerciseName")  # name of specific exercise if one is agreed upon

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