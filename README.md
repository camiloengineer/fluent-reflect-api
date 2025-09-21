# Fluent Reflect API

FastAPI backend for code execution, AI chat, and challenge generation using Judge0 and OpenAI APIs.

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
# Create .env file with:
JUDGE0_API_KEY=your_judge0_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

3. **Activate virtual environment (if using one):**
```bash
source venv/bin/activate
```

4. **Run development server:**
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
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key for chat and challenges | `sk-abc123def456...` |

**How to get API Keys:**

**Judge0 API Key:**
1. Go to [RapidAPI Judge0 CE](https://rapidapi.com/judge0-official/api/judge0-ce/)
2. Subscribe to the free plan
3. Copy your API key from the dashboard

**OpenAI API Key:**
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

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

### 4. Chat with AI
```http
POST /api/chat
```

**Request Headers:**
```
Content-Type: application/json
```

**Request Body (Required):**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Explain how recursion works in programming"
    }
  ],
  "temperature": 0.5,
  "max_tokens": 400,
  "presence_penalty": 0,
  "frequency_penalty": 0.2,
  "top_p": 0.9
}
```

**Request Schema:**
- `messages` (array, required): Array of chat messages with role and content
- `temperature` (float, optional): Response creativity (0.0-1.0, default: 0.5)
- `max_tokens` (integer, optional): Maximum response length (default: 400)
- `presence_penalty` (float, optional): Penalty for new topics (default: 0)
- `frequency_penalty` (float, optional): Penalty for repetition (default: 0.2)
- `top_p` (float, optional): Nucleus sampling parameter (default: 0.9)

**Response - Success:**
```json
{
  "response": "## Recursión en Programación\n\n**Recursión** es una técnica de programación donde una función se llama a sí misma para resolver un problema dividiéndolo en subproblemas más pequeños y similares.\n\n### Ejemplo básico:\n```javascript\nfunction factorial(n) {\n  if (n <= 1) return 1;\n  return n * factorial(n - 1);\n}\n```\n\n> **Tip:** Siempre define un caso base para evitar recursión infinita."
}
```

**Note:** All chat responses are formatted in **Markdown** for easy frontend rendering with syntax highlighting and formatting.

**Response - Rate Limited:**
```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

### 5. Generate Programming Challenge
```http
POST /api/generate-challenge
```

**Request Headers:**
```
Content-Type: application/json
```

**Request Body (Required):**
```json
{
  "language": "javascript",
  "difficulty": "easy",
  "topic": "arrays",
  "chat_context": [
    {
      "role": "user",
      "content": "I want to practice array manipulation"
    }
  ]
}
```

**Request Schema:**
- `language` (string, optional): Programming language (default: "javascript")
- `difficulty` (string, optional): Challenge difficulty: "easy", "medium", "hard" (default: "easy")
- `topic` (string, optional): Programming topic (arrays, algorithms, strings, etc.)
- `chat_context` (array, optional): Previous chat messages for context

**Response - Success:**
```json
{
  "challenge_id": "array_sum_easy_123",
  "title": "Array Sum Calculator",
  "description": "Create a function that takes an array of numbers and returns the sum of all elements.",
  "template_code": "function calculateSum(numbers) {\n  // Your code here\n  return 0;\n}"
}
```

**Response Schema:**
- `challenge_id` (string): Unique identifier for the challenge
- `title` (string): Challenge title
- `description` (string): Detailed problem description
- `template_code` (string): Starting template code for the challenge

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

### Chat Example
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What is the time complexity of bubble sort?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 300
  }'
```

### Challenge Generation Example
```bash
curl -X POST "http://localhost:8000/api/generate-challenge" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "difficulty": "medium",
    "topic": "algorithms"
  }'
```

## 📖 Swagger Documentation

**Interactive API docs available at:**
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

## 🔧 Frontend Integration

### Code Execution
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

### AI Chat
```javascript
const chatWithAI = async (messages, options = {}) => {
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: messages,
      temperature: options.temperature || 0.5,
      max_tokens: options.maxTokens || 400,
      ...options
    })
  });

  return await response.json();
};

// Usage
const messages = [
  { role: "user", content: "Explain async/await in JavaScript" }
];
const chatResult = await chatWithAI(messages);
console.log(chatResult.response); // Returns Markdown formatted response

// Frontend can then render the Markdown as HTML
// Example with a Markdown library like 'marked':
// const htmlContent = marked(chatResult.response);
```

### Challenge Generation
```javascript
const generateChallenge = async (language = "javascript", difficulty = "easy", topic = null) => {
  const response = await fetch('http://localhost:8000/api/generate-challenge', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      language: language,
      difficulty: difficulty,
      topic: topic
    })
  });

  return await response.json();
};

// Usage
const challenge = await generateChallenge("python", "medium", "algorithms");
console.log(challenge.title);
console.log(challenge.description);
console.log(challenge.template_code);
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