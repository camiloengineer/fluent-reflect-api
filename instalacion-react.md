# Instalación y Configuración - React + GPT-5-Mini API

## 📋 Requisitos Previos

### 1. Crear proyecto React
```bash
npx create-react-app gpt5-react-app
cd gpt5-react-app
npm install
```

### 2. Instalar dependencias necesarias
```bash
npm install axios
```

## 🔧 Configuración de la API

### Token de Acceso (Hardcodeado - Solo Desarrollo)
```javascript
// config/api.js
const API_CONFIG = {
  OPENAI_API_KEY: "sk-your-openai-api-key-here", // ⚠️ HARDCODEADO PARA PRUEBAS
  BASE_URL: "https://api.openai.com/v1/responses",
  HEADERS: {
    "Authorization": "Bearer sk-your-openai-api-key-here",
    "Content-Type": "application/json"
  }
};

export default API_CONFIG;
```

## 📡 Implementación del Cliente API

### 1. Servicio API (services/gpt5Service.js)
```javascript
import axios from 'axios';
import API_CONFIG from '../config/api';

class GPT5Service {
  async sendPrompt(userPrompt, options = {}) {
    const payload = {
      model: "gpt-5-mini",
      input: userPrompt,
      temperature: options.temperature || 0.2,
      max_output_tokens: options.maxTokens || 800,
      truncation: "auto",
      // Opcional: control de razonamiento
      reasoning: {
        effort: options.effort || "low" // minimal | low | medium | high
      }
    };

    try {
      const response = await axios.post(
        API_CONFIG.BASE_URL,
        payload,
        {
          headers: API_CONFIG.HEADERS,
          timeout: 60000
        }
      );

      // Extraer texto de la respuesta estructurada
      return this.extractTextFromResponse(response.data);
    } catch (error) {
      console.error('Error calling GPT-5-mini API:', error);
      throw error;
    }
  }

  extractTextFromResponse(data) {
    const texts = [];

    for (const item of data.output || []) {
      if (item.type === "message") {
        for (const part of item.content || []) {
          if (part.type === "output_text") {
            texts.push(part.text || "");
          }
        }
      }
    }

    return texts.join("\n");
  }
}

export default new GPT5Service();
```

### 2. Hook personalizado (hooks/useGPT5.js)
```javascript
import { useState } from 'react';
import GPT5Service from '../services/gpt5Service';

export const useGPT5 = () => {
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState('');
  const [error, setError] = useState(null);

  const sendPrompt = async (prompt, options) => {
    setLoading(true);
    setError(null);

    try {
      const result = await GPT5Service.sendPrompt(prompt, options);
      setResponse(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResponse('');
    setError(null);
  };

  return {
    loading,
    response,
    error,
    sendPrompt,
    reset
  };
};
```

## 🎯 Componente de Ejemplo

### Componente Principal (components/GPTChat.js)
```javascript
import React, { useState } from 'react';
import { useGPT5 } from '../hooks/useGPT5';

const GPTChat = () => {
  const [prompt, setPrompt] = useState('');
  const { loading, response, error, sendPrompt, reset } = useGPT5();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    try {
      await sendPrompt(prompt, {
        temperature: 0.2,
        maxTokens: 1000,
        effort: 'low'
      });
    } catch (err) {
      console.error('Error:', err);
    }
  };

  return (
    <div className="gpt-chat">
      <h2>GPT-5-Mini React Client</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Escribe tu prompt aquí..."
            rows={4}
            cols={50}
            disabled={loading}
          />
        </div>

        <div>
          <button type="submit" disabled={loading || !prompt.trim()}>
            {loading ? 'Enviando...' : 'Enviar'}
          </button>
          <button type="button" onClick={reset}>
            Limpiar
          </button>
        </div>
      </form>

      {error && (
        <div className="error">
          <h3>Error:</h3>
          <p>{error}</p>
        </div>
      )}

      {response && (
        <div className="response">
          <h3>Respuesta:</h3>
          <pre>{response}</pre>
        </div>
      )}
    </div>
  );
};

export default GPTChat;
```

### App.js Principal
```javascript
import React from 'react';
import GPTChat from './components/GPTChat';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <GPTChat />
      </header>
    </div>
  );
}

export default App;
```

## 🎨 Estilos CSS (App.css)
```css
.gpt-chat {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.gpt-chat textarea {
  width: 100%;
  margin-bottom: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: monospace;
}

.gpt-chat button {
  margin-right: 10px;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.gpt-chat button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}

.response {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin: 10px 0;
}

.response pre {
  white-space: pre-wrap;
  font-family: 'Courier New', monospace;
  margin: 0;
}
```

## 🚀 Ejecución

### 1. Configurar el token
```javascript
// En config/api.js, reemplaza:
"sk-your-openai-api-key-here"
// Por tu token real de OpenAI
```

### 2. Iniciar la aplicación
```bash
npm start
```

### 3. Abrir en navegador
```
http://localhost:3000
```

## ⚙️ Opciones Avanzadas

### Control de Razonamiento
```javascript
// Para tareas simples (más rápido, menos costo)
await sendPrompt("Hola mundo", { effort: "minimal" });

// Para tareas complejas (más lento, mayor calidad)
await sendPrompt("Resuelve este algoritmo complejo", { effort: "high" });
```

### Control de Temperature
```javascript
// Más determinista (recomendado para código)
await sendPrompt("Escribe una función", { temperature: 0.1 });

// Más creativo
await sendPrompt("Escribe un poema", { temperature: 0.8 });
```

## ⚠️ Notas de Seguridad

1. **Token Hardcodeado**: Solo para desarrollo/pruebas locales
2. **Producción**: Usar variables de entorno o servicios de secrets
3. **Rate Limits**: Implementar throttling si es necesario
4. **Error Handling**: Manejar errores 401, 403, 429, etc.

## 🔍 Troubleshooting

### Error 401/403
- Verificar que el token sea válido
- Confirmar que el proyecto tiene acceso a GPT-5

### Error 400 (Bad Request)
- Activar `truncation: "auto"`
- Reducir `max_output_tokens`
- Verificar formato del payload

### Timeout
- Aumentar timeout en axios
- Usar `effort: "low"` para respuestas más rápidas