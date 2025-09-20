from pydantic import BaseModel
from typing import Optional, List

class ExecuteRequest(BaseModel):
    language_id: int
    source_code: str
    stdin: Optional[str] = ""

class ExecuteResponse(BaseModel):
    status: Optional[str]
    stdout: Optional[str]
    stderr: Optional[str]
    compile_output: Optional[str]
    time: Optional[str]
    memory: Optional[int]
    exit_code: Optional[int]

class ChatMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.5
    max_tokens: Optional[int] = 400
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0.2
    top_p: Optional[float] = 0.9

class ChatResponse(BaseModel):
    response: str

class ChallengeRequest(BaseModel):
    language: str = "javascript"
    difficulty: Optional[str] = "easy"  # easy, medium, hard
    topic: Optional[str] = None  # arrays, algorithms, strings, etc.
    chat_context: Optional[List[ChatMessage]] = None  # Context from chat conversation

class ChallengeResponse(BaseModel):
    challenge_id: str
    title: str
    description: str
    template_code: str