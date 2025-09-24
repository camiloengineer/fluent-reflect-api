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

### Production Base URL

```
https://fluent-reflect-api-581268440769.us-central1.run.app
```

> Nota: El servicio Cloud Run está configurado como PÚBLICO (`--allow-unauthenticated`) y tiene CORS habilitado para el frontend en producción.

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

### API Base URL (Producción)

El backend está desplegado como servicio público en Cloud Run con CORS configurado. El frontend debe usar:

```javascript
const API_BASE_URL = "https://fluent-reflect-api-581268440769.us-central1.run.app";
```

### CORS Configuration

El backend tiene CORS configurado para permitir requests desde:
- `https://fluent-reflect-app.web.app` (Firebase Hosting)
- `https://fluent-reflect-front-d5vnsr2t6q-uc.a.run.app` (Cloud Run Frontend)
- `http://localhost:3000` y `http://localhost:5173` (desarrollo local)

### Code Execution
```javascript
const API_BASE_URL = "https://fluent-reflect-api-581268440769.us-central1.run.app";

const executeCode = async (languageId, sourceCode, stdin = "") => {
  const response = await fetch(`${API_BASE_URL}/api/execute`, {
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
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
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
  const response = await fetch(`${API_BASE_URL}/api/generate-challenge`, {
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

---

## 🔐 Secret Management (Producción)

En producción las claves NO viven en `.env` ni dentro de la imagen. Se inyectan desde **Secret Manager** al desplegar Cloud Run.

### Secretos actuales
| Nombre Secret Manager | Variable de Entorno | Uso |
|-----------------------|---------------------|-----|
| `OPENAI_API_KEY`      | `OPENAI_API_KEY`    | OpenAI Chat / Challenge |
| `JUDGE0_API_KEY`      | `JUDGE0_API_KEY`    | Judge0 Code Execution |

### Rotación rápida (script automatizado)
```bash
./scripts/quick_prod_update.sh "NUEVA_OPENAI_KEY" "NUEVA_JUDGE0_KEY"
```
Este script automatiza todo el proceso de rotación de claves:
1. ✅ Crea service account dedicado (`fluent-reflect-runtime`) si no existe
2. ✅ Crea los secretos en Secret Manager si faltan
3. ✅ Añade nueva versión de cada secreto (rotación sin downtime)
4. ✅ Concede permisos `secretAccessor` al service account runtime
5. ✅ Actualiza servicio Cloud Run con nuevos secretos
6. ✅ Hace health check para verificar funcionamiento

### Setup inicial de secretos
```bash
./scripts/setup_secrets.sh fr-prod-470013 "OPENAI_KEY" "JUDGE0_KEY"
```
Script más básico que solo gestiona secretos sin deployment.

### Cargar secretos localmente (solo para desarrollo):
```bash
export OPENAI_API_KEY="$(gcloud secrets versions access latest --secret=OPENAI_API_KEY --project fr-prod-470013)"
export JUDGE0_API_KEY="$(gcloud secrets versions access latest --secret=JUDGE0_API_KEY --project fr-prod-470013)"
```

### Nunca hacer:
- Comitear claves reales en `.env`.
- Pegar las claves en issues / PR / README.

---

## ☁️ Cloud Run Deployment (Pipeline)

El despliegue se realiza con **Cloud Build** usando `cloudbuild.yaml` que:
1. Construye la imagen y la sube a Artifact Registry.
2. Ejecuta `gcloud run deploy` con `--set-secrets`.
3. Usa service account dedicado: `fluent-reflect-runtime`.

Despliegue manual (si necesitas forzar sin build):
```bash
gcloud run services update fluent-reflect-api \
  --project fr-prod-470013 \
  --region us-central1 \
  --service-account fluent-reflect-runtime@fr-prod-470013.iam.gserviceaccount.com \
  --set-secrets OPENAI_API_KEY=OPENAI_API_KEY:latest,JUDGE0_API_KEY=JUDGE0_API_KEY:latest
```

### Health check público
```bash
curl -i https://fluent-reflect-api-581268440769.us-central1.run.app/health
```

---

## 🛡️ IAM & Seguridad

Roles clave mínimos (sujeto a endurecimiento posterior):
| Principal | Rol principal |
|-----------|--------------|
| Cloud Build SA | Artifact Registry (writer), Cloud Run deploy |
| Runtime SA (`fluent-reflect-runtime`) | Secret Manager accessor, Logging writer |
| Usuario humano | `iam.serviceAccountUser` sobre runtime SA |

Para auditoría de env vars inyectadas:
```bash
gcloud run services describe fluent-reflect-api \
  --project fr-prod-470013 --region us-central1 \
  --format='yaml(spec.template.spec.containers[0].env)'
```

---

## 🧪 Troubleshooting Rápido

| Síntoma | Causa Probable | Acción |
|---------|----------------|--------|
| 403 a `/health` sin token | Servicio privado | Añadir header con identity token |
| Error missing API key | Secret no inyectado | Revisar `--set-secrets` y roles secretAccessor |
| Port not ready | CMD sin expansión de `$PORT` | Usar shell form en Docker (`/bin/sh -c ...`) |
| Artifact Registry DENIED | IAM incompleto en `gcf-artifacts` | Añadir roles reader/writer a SAs |

Logs en tiempo real:
```bash
gcloud logs tail --project fr-prod-470013 --region us-central1 --service fluent-reflect-api
```

---

## 🗺️ Roadmap / Next Steps (Opcional)
| Feature | Estado | Notas |
|---------|--------|-------|
| Tests unitarios básicos | Pendiente | Añadir para servicios judge0/openai |
| API Gateway / auth central | Evaluar | Si crece número de consumidores |
| Rate limiting granular | Parcial | Mejorar por IP / user token |
| Hardening IAM | En curso | Reducir roles amplios tras estabilizar |

---

## ✅ Estado Actual Producción
| Item | Estado |
|------|--------|
| Despliegue Cloud Run | OK |
| Secrets (Secret Manager) | OK, rotación via script |
| Service Account dedicado | OK (`fluent-reflect-runtime`) |
| Acceso público | Restringido (privado con identity token) |
| CORS | Restringido a origen frontend configurado |
