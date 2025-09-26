# 🤖 CLAUDE.md - Backend Stateless Rules

## 📋 API ENDPOINT: `/api/chat`

### 🔄 REQUEST SCHEMA (camelCase - Frontend)
```typescript
interface ChatRequest {
  messages: ChatMessage[]              // Conversación completa
  languageId?: number = 97            // ID del lenguaje (97 = JavaScript)
  exerciseActive?: boolean = false    // true = hay ejercicio activo, false = sin ejercicio
  currentCode?: string = ""           // 📝 CÓDIGO ACTUAL DEL EDITOR MONACO (contexto clave)
  automatic?: boolean = false         // true = prompt automático del frontend
  exerciseName?: string = null        // Nombre específico del ejercicio (para /generate-challenge)

  // 🆕 NUEVOS CAMPOS PARA VEREDICTO AUTOMÁTICO
  finished?: boolean = false          // true = usuario terminó ejercicio, solicita veredicto (REQUIERE automatic=true)
  executionOutput?: string = ""       // Output de console.log/print del código ejecutado

  temperature?: number = 0.5
  maxTokens?: number = 400
  presencePenalty?: number = 0
  frequencyPenalty?: number = 0.2
  topP?: number = 0.9
}
```

### 📤 RESPONSE SCHEMA (camelCase - Frontend)
```typescript
interface ChatResponse {
  response: string                    // Respuesta del asistente
  canGenerateExercise: boolean        // true = ejercicio específico acordado, listo para generar
  exerciseName: string | null         // Nombre del ejercicio acordado (si aplica)
}
```

### 🔄 BACKEND INTERNAL SCHEMA (snake_case)
```python
class ChatRequest(CamelCaseModel):
    messages: List[ChatMessage]
    language_id: Optional[int] = 97
    exercise_active: Optional[bool] = False
    current_code: Optional[str] = ""
    automatic: Optional[bool] = False
    exercise_name: Optional[str] = None

    # 🆕 CAMPOS PARA VEREDICTO AUTOMÁTICO
    finished: Optional[bool] = False
    execution_output: Optional[str] = ""

    # ... otros campos internos en snake_case
```

## 🎯 REGLAS STATELESS DEL BACKEND

### ❌ COMBINACIONES IMPOSIBLES (camelCase)
```typescript
// NUNCA debe ocurrir:
{
  canGenerateExercise: true,
  exerciseName: null               // Si canGenerateExercise=true, DEBE haber exerciseName
}

// NUNCA debe ocurrir:
{
  exerciseActive: true,
  canGenerateExercise: true       // Si hay ejercicio activo, NO se puede generar otro
}

// NUNCA debe ocurrir:
{
  automatic: true,
  canGenerateExercise: true       // Los prompts automáticos NUNCA generan ejercicios
}

// 🆕 NUNCA debe ocurrir:
{
  finished: true,
  automatic: false                // Si finished=true, DEBE ser automatic=true
}
```

### ✅ REGLAS DE LÓGICA STATELESS

#### 1. **PROMPTS AUTOMÁTICOS** (`automatic: true`)
```typescript
REQUEST: { automatic: true }
RESPONSE: { canGenerateExercise: false, exerciseName: null }
```
- **SIEMPRE** retorna `canGenerateExercise: false`
- Son mensajes del sistema, no acuerdos de ejercicios

#### 2. **EJERCICIO ACTIVO** (`exerciseActive: true`)
```typescript
REQUEST: { exerciseActive: true }
RESPONSE: { canGenerateExercise: false, exerciseName: null }
```
- **NUNCA** permite generar nuevo ejercicio si hay uno activo
- El usuario está trabajando en un ejercicio existente

#### 3. **SIN EJERCICIO ACTIVO** (`exerciseActive: false` y `automatic: false`)
```typescript
REQUEST: { exerciseActive: false, automatic: false }
RESPONSE: {
  canGenerateExercise: true/false,  // Depende si se detectó ejercicio específico
  exerciseName: "NombreEjercicio"   // Solo si se acordó ejercicio específico
}
```
- **ÚNICA** condición donde `canGenerateExercise` puede ser `true`
- Requiere detección de ejercicio específico en la respuesta del asistente

#### 4. **🆕 VEREDICTO DE EJERCICIO** (`finished: true`)
```typescript
REQUEST: {
  finished: true,
  automatic: true,        // OBLIGATORIO
  exerciseName: "FizzBuzz",
  currentCode: "...",
  executionOutput: "..."
}
RESPONSE: {
  canGenerateExercise: false,       // NUNCA true para veredictos
  exerciseName: null,
  response: "🏆 VEREDICTO: APROBADO/REPROBADO..."
}
```
- **SIEMPRE** retorna `canGenerateExercise: false`
- Evalúa coherencia entre código + output + ejercicio
- Respuesta incluye veredicto detallado de "Nemesis"

## 🔄 TRANSFORMACIÓN camelCase ↔ snake_case

### 🎯 ESTÁNDAR DE API
- **Frontend/API**: Usa **camelCase** (estándar JSON/JavaScript)
- **Backend/Python**: Usa **snake_case** internamente (estándar Python)
- **Transformación automática**: Pydantic maneja la conversión

### 📝 EJEMPLOS DE TRANSFORMACIÓN
```typescript
// Frontend envía (camelCase):
{
  "languageId": 97,
  "exerciseActive": false,
  "currentCode": "function test() {}",
  "exerciseName": "FizzBuzz",
  "canGenerateExercise": true
}

// Backend procesa internamente (snake_case):
{
  "language_id": 97,
  "exercise_active": false,
  "current_code": "function test() {}",
  "exercise_name": "FizzBuzz",
  "can_generate_exercise": true
}
```

### ✅ COMPATIBILIDAD
- ✅ Frontend puede enviar **camelCase** (recomendado)
- ✅ Backend acepta **snake_case** (compatibilidad hacia atrás)
- ✅ Response siempre en **camelCase** (para frontend)

## 🔍 DETECCIÓN DE EJERCICIOS ESPECÍFICOS

El backend detecta ejercicios específicos mediante patrones en la respuesta:
- "FizzBuzz" → `exerciseName: "FizzBuzz"`
- "Reverse String" → `exerciseName: "Reverse String"`
- "Palindrome" → `exerciseName: "Palindrome"`
- "Find Maximum" → `exerciseName: "Find Maximum"`

## 🚀 FLUJO DE TRABAJO

### 1. **Inicio de Sesión**
```typescript
// Frontend envía automáticamente (camelCase):
{
  automatic: true,
  exerciseActive: false,
  messages: [{ role: "user", content: "INIT_INTERVIEW: ..." }]
}

// Backend responde (camelCase):
{
  canGenerateExercise: false,  // NUNCA true para automático
  response: "Hola, soy Carlos... ¿Te parece FizzBuzz?"
}
```

### 2. **Usuario Acepta Ejercicio**
```typescript
// Usuario responde "sí" o "acepto FizzBuzz" (camelCase):
{
  automatic: false,
  exerciseActive: false,
  messages: [... conversación completa ...]
}

// Backend detecta ejercicio específico (camelCase):
{
  canGenerateExercise: true,   // ✅ Acordado ejercicio específico
  exerciseName: "FizzBuzz",    // ✅ Ejercicio detectado
  response: "Perfecto! Para FizzBuzz..."
}
```

### 3. **Frontend Genera Ejercicio**
```typescript
// Frontend llama a /generate-challenge con (camelCase):
{
  exerciseName: "FizzBuzz",    // Del response anterior
  language: "javascript",
  chatContext: [...]           // Context completo
}
```

### 4. **Ejercicio Activo**
```typescript
// Todas las requests durante el ejercicio (camelCase):
{
  automatic: false,
  exerciseActive: true,        // ✅ Ejercicio en progreso
  currentCode: "function fizz...",
  exerciseName: "FizzBuzz"
}

// Backend SIEMPRE responde (camelCase):
{
  canGenerateExercise: false, // ✅ NUNCA mientras hay ejercicio activo
  exerciseName: null
}
```

## 🔗 INTEGRACIÓN CON `/api/generate-challenge`

```typescript
interface ChallengeRequest {
  language: string = "javascript"
  difficulty?: string = "easy"
  topic?: string = null
  exerciseName?: string = null      // ✅ camelCase: Nombre del ejercicio acordado
  chatContext?: ChatMessage[] = []  // ✅ camelCase: Contexto de la conversación
}
```

## ⚠️ COMANDOS DE DESARROLLO

```bash
# Iniciar servidor
./venv/bin/python -m uvicorn app.main:app --reload

# Probar API (campos actualizados)
python3 test_new_api.py

# Verificar lógica automática
python3 test_automatic_logic.py

# Probar transformación camelCase
python3 test_camelcase_api.py

# Probar funcionalidad de veredicto
python3 test_verdict_functionality.py
```

## 📝 CONTEXTO DEL CÓDIGO ACTUAL (`currentCode`)

### 🎯 PROPÓSITO
El campo `currentCode` (camelCase) contiene el código actual del editor Monaco del frontend. Es **fundamental** para que el asistente entienda el contexto específico del usuario.

### 📋 EJEMPLO DE USO
```typescript
// Código del editor Monaco (camelCase):
{
  currentCode: `function reverseString(str) {
  // ✍️ TU CÓDIGO AQUÍ

}

// Test Cases (ejecutables)
console.log(reverseString('hello')); // Esperado: 'olleh'`
}
```

### 🎯 COMPORTAMIENTO DEL ASISTENTE
Cuando `currentCode` está presente, el asistente:
- ✅ Analiza el código línea por línea
- ✅ Menciona elementos específicos (funciones, variables, comentarios)
- ✅ Identifica qué está implementado y qué falta
- ✅ Da feedback específico al código actual
- ✅ Usa los test cases para explicar el objetivo

### 🔍 ELEMENTOS QUE DETECTA
- Nombres de funciones (`reverseString`)
- Comentarios específicos (`// TU CÓDIGO AQUÍ`)
- Variables definidas (`let result = ""`)
- Test cases (`console.log(...)`)
- Ejemplos de entrada/salida (`'hello'` → `'olleh'`)

## 📝 NOTAS IMPORTANTES

1. **Backend Stateless**: Toda la lógica se basa en el request actual, no hay estado guardado
2. **Campos en Inglés**: Todos los campos han sido migrados de español a inglés
3. **Lógica Defensiva**: Múltiples validaciones para evitar estados inconsistentes
4. **Detección Automática**: El backend detecta ejercicios específicos automáticamente
5. **Prompts Automáticos**: Son transparentes al usuario, solo el frontend los maneja
6. **📝 Contexto de Código**: El asistente siempre analiza el `current_code` cuando está disponible

## 🔧 VARIABLES DE ENTORNO

### 📋 CONFIGURACIÓN REQUERIDA
```bash
# API Keys para servicios externos
JUDGE0_API_KEY=your_judge0_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# CORS origins (comma-separated)
ALLOWED_ORIGINS=https://fluent-reflect-front-d5vnsr2t6q-uc.a.run.app,http://localhost:666
```

### 🔐 MANEJO DE SECRETOS

**IMPORTANTE**: En producción, las API keys se almacenan en Google Secret Manager y se inyectan automáticamente en tiempo de deploy. El archivo `.env` es solo para desarrollo local.

**Para desarrollo local**, las keys reales se cargan usando gcloud:
```bash
export JUDGE0_API_KEY="$(gcloud secrets versions access latest --secret=JUDGE0_API_KEY --project fr-prod-470013)"
export OPENAI_API_KEY="$(gcloud secrets versions access latest --secret=OPENAI_API_KEY --project fr-prod-470013)"
```

### 🎯 CORS CONFIGURATION
- **Producción**: `https://fluent-reflect-front-d5vnsr2t6q-uc.a.run.app`
- **Desarrollo local**: `http://localhost:666`
- Se pueden agregar múltiples origins separados por comas

---
*Generado por Claude Code - Especificación completa del backend stateless*