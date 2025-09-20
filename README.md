# Fluent Reflect API

FastAPI backend for code execution using Judge0 API.

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
# Create .env file with:
JUDGE0_API_KEY=your_judge0_api_key_here
```

3. **Run development server:**
```bash
uvicorn app.main:app --reload --port 8000
```

4. **Run production server:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📋 Required Secrets/Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `JUDGE0_API_KEY` | ✅ Yes | RapidAPI key for Judge0 CE | `abc123def456...` |

**How to get Judge0 API Key:**
1. Go to [RapidAPI Judge0 CE](https://rapidapi.com/judge0-official/api/judge0-ce/)
2. Subscribe to the free plan
3. Copy your API key from the dashboard

## 🔗 API Endpoints

### Base URL
```
http://localhost:8000
```

### 1. Root Endpoint
```http
GET /
```

**Response:**
```json
{
  "message": "Fluent Reflect API is running"
}
```

### 2. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### 3. Execute Code (Main Endpoint)
```http
POST /api/execute
```

**Request Headers:**
```
Content-Type: application/json
```

**Request Body (Required):**
```json
{
  "language_id": 63,
  "source_code": "console.log('Hello World')",
  "stdin": "optional input data"
}
```

**Request Schema:**
- `language_id` (integer, required): Language ID from supported languages
- `source_code` (string, required): Code to execute
- `stdin` (string, optional): Input data for the program

**Response - Success:**
```json
{
  "status": "Accepted",
  "stdout": "Hello World\n",
  "stderr": null,
  "compile_output": null,
  "time": "0.001",
  "memory": 1024,
  "exit_code": 0
}
```

**Response - Compilation Error:**
```json
{
  "status": "Compilation Error",
  "stdout": null,
  "stderr": null,
  "compile_output": "main.cpp:1:1: error: expected expression\n",
  "time": null,
  "memory": null,
  "exit_code": 1
}
```

**Response - Runtime Error:**
```json
{
  "status": "Runtime Error (NZEC)",
  "stdout": null,
  "stderr": "Traceback (most recent call last):\n  File \"main.py\", line 1, in <module>\n    print(1/0)\nZeroDivisionError: division by zero\n",
  "compile_output": null,
  "time": "0.001",
  "memory": 1024,
  "exit_code": 1
}
```

**Response - Server Error:**
```json
{
  "detail": "Execution failed: Connection timeout"
}
```

**Response Schema:**
- `status` (string): Execution status from Judge0
- `stdout` (string|null): Program output
- `stderr` (string|null): Error output
- `compile_output` (string|null): Compilation errors
- `time` (string|null): Execution time in seconds
- `memory` (integer|null): Memory used in KB
- `exit_code` (integer|null): Program exit code

## 🗂️ Supported Languages

| Language | ID | Example |
|----------|----|---------|
| **JavaScript** | 63 | `console.log('Hello')` |
| **Python 3** | 71 | `print('Hello')` |
| **TypeScript** | 74 | `console.log('Hello')` |
| **Rust** | 73 | `fn main() { println!("Hello"); }` |
| **Go** | 60 | `package main\nfunc main() { fmt.Println("Hello") }` |
| **C** | 50 | `#include<stdio.h>\nint main(){ printf("Hello"); }` |
| **C++** | 54 | `#include<iostream>\nint main(){ std::cout<<"Hello"; }` |
| **Java** | 62 | `class Main{ public static void main(String[] a){ System.out.println("Hello"); }}` |
| **C#** | 51 | `using System; class Program { static void Main() { Console.WriteLine("Hello"); }}` |

## 📊 Example Usage

### JavaScript Example
```bash
curl -X POST "http://localhost:8000/api/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "language_id": 63,
    "source_code": "const name = \"World\";\nconsole.log(`Hello ${name}!`);",
    "stdin": ""
  }'
```

### Python with Input
```bash
curl -X POST "http://localhost:8000/api/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "language_id": 71,
    "source_code": "name = input()\nprint(f\"Hello {name}!\")",
    "stdin": "Alice"
  }'
```

### C++ Example
```bash
curl -X POST "http://localhost:8000/api/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "language_id": 54,
    "source_code": "#include<iostream>\nusing namespace std;\nint main(){\n    cout << \"Hello World!\" << endl;\n    return 0;\n}",
    "stdin": ""
  }'
```

## 📖 Swagger Documentation

**Interactive API docs available at:**
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

## 🔧 Frontend Integration

**Example frontend call:**
```javascript
const executeCode = async (languageId, sourceCode, stdin = "") => {
  const response = await fetch('http://localhost:8000/api/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      language_id: languageId,
      source_code: sourceCode,
      stdin: stdin
    })
  });

  return await response.json();
};

// Usage
const result = await executeCode(63, "console.log('Hello World!')", "");
console.log(result.stdout); // "Hello World!"
```

## 🐳 Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t fluent-reflect-api .
docker run -p 8000:8000 --env-file .env fluent-reflect-api
```