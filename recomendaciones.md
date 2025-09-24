# 🔒 Recomendaciones de Seguridad

## ⚠️ Estado Actual de Seguridad

El backend está desplegado con `--allow-unauthenticated`, lo que significa que es **públicamente accesible** sin autenticación.

### Vulnerabilidades Identificadas

| Vulnerabilidad | Impacto | Severidad |
|----------------|---------|-----------|
| API pública sin auth | Cualquiera puede consumir recursos | 🔴 Alto |
| Exposición de claves OpenAI/Judge0 | Uso no autorizado de servicios pagos | 🔴 Alto |
| Rate limiting básico | Solo por IP, fácil de evadir | 🟡 Medio |
| Sin logging de usuarios | No trazabilidad de uso | 🟡 Medio |

## 🛡️ Recomendaciones de Seguridad

### 1. Implementar Autenticación (Prioridad Alta)

#### Opción A: Firebase Auth + Identity Tokens
```bash
# Remover acceso público
gcloud run services update fluent-reflect-api \
  --project fr-prod-470013 \
  --region us-central1 \
  --no-allow-unauthenticated
```

**Frontend debe obtener identity token:**
```javascript
import { getAuth } from 'firebase/auth';

const getIdToken = async () => {
  const auth = getAuth();
  const user = auth.currentUser;
  if (user) {
    return await user.getIdToken();
  }
  throw new Error('Usuario no autenticado');
};

// Usar token en requests
const response = await fetch(`${API_BASE_URL}/api/chat`, {
  headers: {
    'Authorization': `Bearer ${await getIdToken()}`,
    'Content-Type': 'application/json'
  },
  // ...
});
```

#### Opción B: API Gateway con Auth
- Usar Cloud Endpoints o API Gateway
- Configurar OAuth 2.0 / JWT validation
- Rate limiting por usuario autenticado

### 2. Rate Limiting Mejorado

```python
# Implementar en app/utils/rate_limiter.py
class UserRateLimiter:
    def __init__(self):
        self.user_requests = {}  # {user_id: {timestamp: count}}

    def check_user_limit(self, user_id: str, limit: int = 100):
        """Rate limit por usuario autenticado (100 req/hour)"""
        # Implementation...
```

### 3. Logging y Monitoreo

```python
# Agregar logging estructurado
import logging
import json

def log_api_usage(user_id: str, endpoint: str, tokens_used: int = 0):
    log_data = {
        "user_id": user_id,
        "endpoint": endpoint,
        "tokens_used": tokens_used,
        "timestamp": datetime.utcnow().isoformat()
    }
    logging.info(json.dumps(log_data))
```

### 4. Validación de Input Mejorada

```python
from pydantic import validator, Field

class SecureChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., max_items=20)
    max_tokens: int = Field(default=400, le=1000)  # Limitar tokens máximos

    @validator('messages')
    def validate_message_length(cls, v):
        for msg in v:
            if len(msg.content) > 4000:  # Limitar longitud
                raise ValueError('Mensaje demasiado largo')
        return v
```

### 5. Secrets y Environment

```bash
# Usar versiones específicas en lugar de :latest
gcloud run services update fluent-reflect-api \
  --set-secrets OPENAI_API_KEY=OPENAI_API_KEY:1 \
  --set-secrets JUDGE0_API_KEY=JUDGE0_API_KEY:1
```

### 6. Network Security

```bash
# Configurar VPC Connector (opcional)
gcloud run services update fluent-reflect-api \
  --vpc-connector projects/fr-prod-470013/locations/us-central1/connectors/api-connector \
  --vpc-egress private-ranges-only
```

## 🚀 Plan de Implementación

### Fase 1: Autenticación Básica (1-2 días)
1. [ ] Configurar Firebase Auth en frontend
2. [ ] Agregar middleware de validación de tokens
3. [ ] Remover `--allow-unauthenticated`
4. [ ] Testing con usuarios autenticados

### Fase 2: Rate Limiting Avanzado (1 día)
1. [ ] Implementar rate limiting por usuario
2. [ ] Agregar límites diferenciados por tier de usuario
3. [ ] Dashboard de uso por usuario

### Fase 3: Monitoring y Logging (1 día)
1. [ ] Structured logging para todas las requests
2. [ ] Alertas por uso excesivo
3. [ ] Dashboard de métricas en Cloud Monitoring

### Fase 4: Hardening Adicional (1 día)
1. [ ] Input validation estricta
2. [ ] VPC networking (si se requiere)
3. [ ] Backup y recovery procedures

## 🔧 Scripts de Transición

### Migrar a Autenticado
```bash
#!/bin/bash
# scripts/migrate_to_auth.sh
set -e

echo "Removiendo acceso público..."
gcloud run services update fluent-reflect-api \
  --project fr-prod-470013 \
  --region us-central1 \
  --no-allow-unauthenticated

echo "Verificando acceso restringido..."
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' \
  https://fluent-reflect-api-581268440769.us-central1.run.app/health)

if [[ "$HTTP_CODE" == "403" ]]; then
  echo "✅ API ahora requiere autenticación"
else
  echo "❌ Error: API aún accesible públicamente ($HTTP_CODE)"
  exit 1
fi
```

### Testing con Auth
```bash
#!/bin/bash
# scripts/test_with_auth.sh
TOKEN=$(gcloud auth print-identity-token)

curl -H "Authorization: Bearer $TOKEN" \
  https://fluent-reflect-api-581268440769.us-central1.run.app/health
```

## 💡 Consideraciones Adicionales

### Costos
- Identity tokens: Gratis en Firebase Auth
- Cloud Run: Mismo costo (requests autenticadas)
- API Gateway: ~$3 per million calls (si se usa)

### UX Impact
- Usuario debe autenticarse antes de usar la app
- Tokens expiran (necesita refresh automático)
- Manejo de errores 401/403

### Alternativa Temporal
Si no puedes implementar auth inmediatamente, considera:
- API Key simple en headers
- Whitelist de IPs conocidas
- Rate limiting más agresivo por IP

---

**Nota:** Estas recomendaciones están ordenadas por prioridad. La autenticación debe implementarse primero para cerrar la vulnerabilidad principal.