from pydantic import BaseModel
from typing import Optional

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