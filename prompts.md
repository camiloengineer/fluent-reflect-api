# Prompt Architecture & Efficiency Review

## 1. Identidad del Entrevistador (Nemesis)
- **Nombre único:** Nemesis (sin acento). No se presentan múltiples entrevistadores; es un MVP.
- **Tono:** Cortante, directo, sin small talk ni preguntas superfluas. Las pistas son breves y quirúrgicas.
- **Flujo natural:** Las respuestas deben sonar fluidas. Ejemplo correcto: `"Hola, soy Nemesis, vamos directo al nivel de ejercicios."` Ejemplo incorrecto (evitar formato enumerado o robótico): `"1. Hola, soy Nemesis. 2. Te puedo ofrecer..."`

## 2. Prompt base del chat (`SYSTEM_PROMPT`)
- Contextualiza a Nemesis como entrevistador.
- Refuerza la prioridad de proponer ejercicios concretos.
- Añade instrucciones dinámicas según el lenguaje y estado del ejercicio.
- **Eficiencia:** Se mantiene compacto (< 500 tokens) pero cubre actitud, formato y reglas de interacción. Los anexos (código actual, estado del ejercicio) sólo se agregan cuando existen datos, evitando consumo innecesario.

### Ejemplo de respuesta esperada
```
Hola, soy Nemesis. Vamos al grano: ¿practicamos FizzBuzz para empezar?
```

## 3. Prompts automáticos especializados
| Tipo | Objetivo | Notas de eficiencia |
|------|----------|---------------------|
| `INIT_INTERVIEW` | Saludo inicial cuando la sesión comienza automáticamente. | Mensaje corto, un único ejercicio sugerido. |
| `HINT_REQUEST` | Dar una pista sobre el código actual. | Referencia directa a variables/funciones relevantes; evita bloques largos. |
| `EXERCISE_END` | Feedback al abandonar un ejercicio. | 5 pasos concretos que cierran el flujo sin reabrir la conversación. |
| `EXERCISE_VERDICT` | Dictamen final del ejercicio. | Complementado con el razonamiento privado descrito abajo. |

### Cadena de razonamiento (`build_verdict_reasoning_prompt`)
- Siete pasos derivados de `chain-of-thinking.txt` garantizan un veredicto estricto.
- Sólo se activa cuando `finished=True` y `automatic=True`, manteniendo el backend stateless.
- **Token efficiency:** El prompt se adjunta como mensaje `system` adicional únicamente en veredictos.
- **UX/UI:** El asistente entrega el veredicto y termina; no hay postveredicto.

## 4. Plantillas de ejercicios generadas
- Formato inspirado en HackerRank:
  1. Nombre del ejercicio como comentario.
  2. Descripción breve.
  3. Función vacía con comentario `// ✍️ TU CÓDIGO AQUÍ` o equivalente en Python.
  4. Bloque comentado de ejemplos entrada/salida.
  5. Sección de restricciones (`// 🛑 Restricciones:`).
  6. Test cases ejecutables preparados para la consola.
- **Integridad:** Las secciones aparecen siempre, incluso si el modelo no provee constraints (se agrega recordatorio).
- **Consistencia:** Reutiliza los `test_cases` y `constraints` devueltos por OpenAI para evitar repetición manual.

### Fragmento generado (JavaScript)
```javascript
// 🧪 Ejercicio: Suma A+B
// 📋 Descripción: Dado dos enteros a y b, retorna a + b.

function sum(a, b) {
  // ✍️ TU CÓDIGO AQUÍ
}

// 📥 Ejemplos de Entrada/Salida:
// Entrada: 2, 3  →  Salida esperada: 5
// Entrada: 4, 7  →  Salida esperada: 11

// 🛑 Restricciones:
// - 1 ≤ a, b ≤ 10^4
// - Los parámetros siempre son enteros

// Test Cases (ejecutables)
console.log(sum(2, 3)); // Esperado: 5
console.log(sum(4, 7)); // Esperado: 11
```

## 5. Cohesión y consumo de tokens
- Todos los prompts comparten el lenguaje (`Spanish`), tono y referencias a Nemesis para coherencia.
- Componentes condicionales (código actual, ejemplos, restricciones) sólo se incluyen cuando hay datos → evita inflar mensajes.
- El razonamiento de veredicto opera como prompt interno; no contamina la respuesta final.
- Las plantillas reutilizan metadatos generados (title, description, test cases), reduciendo repeticiones en llamadas posteriores.

## 6. Ejemplos end-to-end
**Escenario:** Usuario termina ejercicio `FizzBuzz`.
1. Frontend envía `automatic=True`, `finished=True`, `currentCode`, `executionOutput`.
2. Backend adjunta `EXERCISE_VERDICT` + razonamiento interno.
3. Respuesta esperada:
   ```markdown
   🏆 **VEREDICTO: APROBADO**

   **Paso 1 - Implementación:** Código completo, maneja múltiplos de 3 y 5.
   **Paso 2 - Output:** Consola muestra secuencia correcta hasta 15.
   **Paso 3 - Coherencia:** Lógica y salida coinciden con FizzBuzz.

   **Decisión Final:** Implementación coincide al 100% con el enunciado.
   ```
4. Conversación concluye tras el veredicto (stateless).

## 7. Verificación
- Prompt structure asegurada vía tests unitarios:
  - `test_verdict_chain_prompt.py` valida secciones clave del reasoning.
  - `test_challenge_template_format.py` confirma presencia de metadata y restricciones en plantillas.
- *Nota:* `pytest` no está instalado en el entorno actual (`pytest: command not found`). Ejecutar las pruebas tras instalarlo para validar localmente.

## 8. Recomendaciones operativas
- Mantener Nemesis como única voz hasta que se soporte multientrevistador.
- Revisar periódicamente el tamaño de los prompts cuando se escalen a modelos más grandes (o4) para preservar eficiencia.
- Si se agregan nuevos lenguajes, replicar el formato de plantillas respetando secciones y comentarios localizados.
- Evitar cambios en firmas de endpoints: todas las mejoras residen en prompts y contenido generado.
