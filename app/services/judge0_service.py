import httpx
import os
from app.utils.decoder import decode_base64
from dotenv import load_dotenv

load_dotenv()

JUDGE0_API = "https://judge0-ce.p.rapidapi.com"

async def get_languages():
    """Get all active languages from Judge0 API"""
    API_KEY = os.getenv("JUDGE0_API_KEY")
    if not API_KEY:
        raise Exception("JUDGE0_API_KEY environment variable not set")

    headers = {
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        "X-RapidAPI-Key": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{JUDGE0_API}/languages",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

# Curated language selection - one stable/LTS version per language
SUPPORTED_LANGUAGES = {
    97: {"name": "JavaScript", "display_name": "JavaScript (Node.js 20 LTS)"},
    100: {"name": "Python", "display_name": "Python 3.12"},
    103: {"name": "C", "display_name": "C (GCC 14.1)"},
    105: {"name": "C++", "display_name": "C++ (GCC 14.1)"},
    91: {"name": "Java", "display_name": "Java 17 LTS"},
    107: {"name": "Go", "display_name": "Go 1.23"},
    108: {"name": "Rust", "display_name": "Rust 1.85"},
    98: {"name": "PHP", "display_name": "PHP 8.3"},
    101: {"name": "TypeScript", "display_name": "TypeScript 5.6"},
    111: {"name": "Kotlin", "display_name": "Kotlin 2.1"},
    112: {"name": "Scala", "display_name": "Scala 3.4"},
    72: {"name": "Ruby", "display_name": "Ruby 2.7"},
    51: {"name": "C#", "display_name": "C# (Mono)"},
    90: {"name": "Dart", "display_name": "Dart 2.19"},
    83: {"name": "Swift", "display_name": "Swift 5.2"},
    99: {"name": "R", "display_name": "R 4.4"},
    82: {"name": "SQL", "display_name": "SQL (SQLite)"}
}

def get_language_name(language_id: int) -> str:
    """Get the language name from language_id"""
    if language_id in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[language_id]["name"]
    return "JavaScript"  # Default fallback

def get_supported_languages():
    """Get list of curated languages for dropdown"""
    return [
        {
            "id": lang_id,
            "name": info["name"],
            "display_name": info["display_name"]
        }
        for lang_id, info in SUPPORTED_LANGUAGES.items()
    ]

async def execute_code(language_id: int, source_code: str, stdin: str = ""):
    """Execute code using Judge0 API - replicates frontend logic"""
    API_KEY = os.getenv("JUDGE0_API_KEY")
    print(f"DEBUG - API_KEY: {API_KEY}")
    if not API_KEY:
        raise Exception("JUDGE0_API_KEY environment variable not set")

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

        # 2. Poll for submission results until completion
        import asyncio
        max_attempts = 30  # Maximum polling attempts
        delay = 1  # Delay between polls in seconds

        for attempt in range(max_attempts):
            result_response = await client.get(
                f"{JUDGE0_API}/submissions/{token}?base64_encoded=true",
                headers=headers
            )
            result_response.raise_for_status()
            result = result_response.json()

            status = result.get("status", {})
            status_id = status.get("id")

            # Status IDs: 1=In Queue, 2=Processing, 3=Accepted, 4=Wrong Answer, 5=Time Limit Exceeded, etc.
            # We continue polling while status is 1 (In Queue) or 2 (Processing)
            if status_id not in [1, 2]:
                break

            print(f"DEBUG - Polling attempt {attempt + 1}, status: {status.get('description')}")
            await asyncio.sleep(delay)

        # 3. Process response (replicating frontend logic from Playground.jsx)
        submission_stdout = result.get("stdout")
        submission_stderr = result.get("stderr")
        submission_compile_output = result.get("compile_output")
        submission_status = result.get("status", {}).get("description")

        # Debug logging
        print(f"DEBUG - stdout: {submission_stdout}")
        print(f"DEBUG - stderr: {submission_stderr}")
        print(f"DEBUG - compile_output: {submission_compile_output}")
        print(f"DEBUG - status: {submission_status}")

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