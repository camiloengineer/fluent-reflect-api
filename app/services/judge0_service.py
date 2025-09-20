import httpx
import os
from app.utils.decoder import decode_base64

JUDGE0_API = "https://judge0-ce.p.rapidapi.com"
API_KEY = os.getenv("JUDGE0_API_KEY")

async def execute_code(language_id: int, source_code: str, stdin: str = ""):
    """Execute code using Judge0 API - replicates frontend logic"""
    headers = {
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        "X-RapidAPI-Key": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        # 1. Submit code to Judge0
        submit_payload = {
            "language_id": language_id,
            "source_code": source_code,
            "stdin": stdin
        }

        submit_response = await client.post(
            f"{JUDGE0_API}/submissions",
            json=submit_payload,
            headers=headers
        )
        submit_response.raise_for_status()
        token = submit_response.json()["token"]

        # 2. Get submission results
        result_response = await client.get(
            f"{JUDGE0_API}/submissions/{token}?base64_encoded=true",
            headers=headers
        )
        result_response.raise_for_status()
        result = result_response.json()

        # 3. Process response (replicating frontend logic from Playground.jsx)
        submission_stdout = result.get("stdout")
        submission_stderr = result.get("stderr")
        submission_compile_output = result.get("compile_output")
        submission_status = result.get("status", {}).get("description")

        # Handle different output scenarios like frontend does
        if submission_compile_output:
            # Compilation error
            return {
                "status": submission_status,
                "stdout": None,
                "stderr": None,
                "compile_output": decode_base64(submission_compile_output),
                "time": None,
                "memory": None,
                "exit_code": result.get("exit_code")
            }
        elif submission_stderr:
            # Runtime error
            return {
                "status": submission_status,
                "stdout": None,
                "stderr": decode_base64(submission_stderr),
                "compile_output": None,
                "time": result.get("time"),
                "memory": result.get("memory"),
                "exit_code": result.get("exit_code")
            }
        else:
            # Success case
            return {
                "status": submission_status,
                "stdout": decode_base64(submission_stdout) if submission_stdout else None,
                "stderr": None,
                "compile_output": None,
                "time": result.get("time"),
                "memory": result.get("memory"),
                "exit_code": result.get("exit_code")
            }