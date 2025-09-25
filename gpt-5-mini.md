Aquí tienes cómo invocar gpt-5-mini desde Python con HTTP puro (sin SDK), usando el endpoint Responses, los encabezados de autenticación correctos y el formato de carga útil recomendado para tareas de código.[1][2]

### Requisitos y endpoint
- Definir la variable de entorno OPENAI_API_KEY con una clave válida y usar autenticación Bearer en cada solicitud HTTP.[1]
- El modelo se invoca por ID "gpt-5-mini" y se recomienda usar el endpoint v1/responses para nuevas integraciones.[2][1]

### Instalación mínima
- Usar la librería requests o httpx; a continuación se muestra con requests para mantener dependencias al mínimo.[1]

```bash
pip install requests
```

### Solicitud básica (requests)
- Ejemplo síncrono: envía un prompt de programación y obtiene texto desde el campo output, sin usar SDK.[1]

```python
import os, requests, json

API_KEY = os.environ["OPENAI_API_KEY"]
BASE_URL = "https://api.openai.com/v1/responses"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": "gpt-5-mini",
    "input": "Escribe una función Python que resuelva Two Sum en O(n) y explica la complejidad.",
    # Opcionales recomendados para código:
    "temperature": 0.2,              # Más determinista para código
    "max_output_tokens": 800,        # Límite de salida
    "truncation": "auto",            # Evita errores por contexto
}

resp = requests.post(BASE_URL, headers=headers, data=json.dumps(payload), timeout=60)
resp.raise_for_status()
data = resp.json()

# Extraer texto agregado desde la estructura 'output'
texts = []
for item in data.get("output", []):
    if item.get("type") == "message":
        for part in item.get("content", []):
            if part.get("type") == "output_text":
                texts.append(part.get("text", ""))

print("\n".join(texts))
```

- La API Responses devuelve un objeto con la matriz output; cada ítem message contiene content con partes output_text, que es lo que se debe concatenar para recuperar el texto final sin depender de atajos del SDK.[1]

### Razonamiento y control de coste
- gpt-5 y la serie o‑* admiten el objeto reasoning; para code challenge breve, usar reasoning.effort="low" o "minimal" prioriza velocidad y costo, y subir a "medium" o "high" en problemas complejos.[3][1]

```python
payload = {
    "model": "gpt-5-mini",
    "input": "Implementa quicksort en Python con pruebas básicas.",
    "reasoning": { "effort": "low" },  # minimal | low | medium | high
    "temperature": 0.2,
    "max_output_tokens": 1000,
    "truncation": "auto",
}
```

- Ajustar temperature en 0.1–0.3 para mayor determinismo en código; top_p es alternativa pero se recomienda modificar uno u otro, no ambos.[1]

### Function calling (herramientas personalizadas)
- Para validar soluciones con un runner propio, exponer una herramienta function en tools; el modelo puede llamar a run_tests con argumentos tipados vía JSON Schema.[4][1]

```python
payload = {
    "model": "gpt-5-mini",
    "instructions": "Escribe una función is_palindrome(s) en Python y prepárala para pruebas.",
    "input": "Devuelve solo el código listo para ejecutar.",
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "run_tests",
                "description": "Ejecuta pruebas unitarias sobre el código y devuelve {passed, report}.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": { "type": "string" }
                    },
                    "required": ["code"],
                    "additionalProperties": False
                }
            }
        }
    ],
    "tool_choice": "auto",
    "temperature": 0.2,
    "truncation": "auto"
}
```

- Al habilitar tools, la respuesta puede incluir llamadas de herramienta que se deben interceptar y resolver del lado del servidor antes de continuar la conversación con previous_response_id o un objeto conversation, según el flujo elegido.[1]

### Buenas prácticas de producción
- Registrar x-request-id y cabeceras de rate limit en cada respuesta para depurar y monitorear cuotas en producción.[1]
- Si se prevé latencia/cola, considerar service_tier con "flex" o "priority" según las necesidades del proyecto, dejando en "auto" por defecto si no se especifica.[1]

### Verificación rápida
- Probar primero con un prompt simple y confirmar que output contiene al menos un ítem message con partes output_text; si hay 401/403, revisar el Bearer token y el proyecto; si hay 400 por longitud, activar truncation="auto" o reducir el contexto.[1]
- Confirmar que el ID del modelo es “gpt-5-mini” dentro del conjunto GPT‑5 soportado y que el proyecto tiene acceso habilitado a la familia GPT‑5.[2]

[1](https://platform.openai.com/docs/api-reference/responses)
[2](https://platform.openai.com/docs/models/gpt-5)
[3](https://platform.openai.com/docs/guides/reasoning)
[4](https://platform.openai.com/docs/guides/function-calling)