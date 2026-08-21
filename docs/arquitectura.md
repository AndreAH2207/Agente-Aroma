# Arquitectura · Asesor de regalos Aroma

## Flujo

```
Cliente (CLI)
   │  "Un regalo para mi papá cervecero, tengo S/100"
   ▼
asesor.py  ──►  Responses API (Foundry)  ──►  Agente "asesor-aroma"
   ▲                                            │  decide qué herramienta usar
   │                                            ▼
   │                        ┌───────────────────┴───────────────────┐
   │                        ▼                                        ▼
   │                 File Search (RAG)                    Function tools (local)
   │                 catalogo-aroma.md                    buscar_productos()
   │                 (qué incluye, FAQ,                   armar_pedido()
   │                  ingredientes)                       catalogo-aroma.json
   │                        │                                        │
   └────────────  respuesta con recomendación + total + enlace WhatsApp
```

## Piezas

| Pieza | Rol |
|-------|-----|
| **Modelo** (`MODEL_DEPLOYMENT_NAME`) | Motor que razona y redacta la recomendación. |
| **Agente** (`asesor-aroma`) | Modelo + instrucciones de sistema + herramientas. Versionado con `create_version`. |
| **File Search (RAG)** | Indexa `catalogo-aroma.md`. Responde sobre qué incluye un box, ingredientes, FAQ y cómo comprar, citando el documento. |
| **buscar_productos** (función) | Filtra el catálogo real por ocasión, categoría y presupuesto. Evita inventar productos/precios. |
| **armar_pedido** (función) | Calcula el total y genera el enlace `wa.me` con el mismo formato del carrito de la web. |
| **Conversación** | `conversation_id` reutilizado = memoria por sesión. |

## Decisión: dos capacidades, una fuente de verdad

- `data/catalogo-aroma.json` alimenta las **funciones** (datos estructurados, cálculos exactos).
- `data/catalogo-aroma.md` alimenta el **RAG** (texto para preguntas abiertas).
- Ambos derivan del mismo catálogo de la tienda, así el agente nunca contradice a la web.

## Bucle de function calling

1. `asesor.py` envía el mensaje del usuario (primera Response).
2. Si la respuesta trae `function_call`, se ejecuta la función en Python y se
   devuelve `function_call_output` en una segunda Response.
3. Se repite hasta `MAX_RONDAS_TOOLS` o hasta obtener texto final.

## Controles y límites

- Validación de argumentos en cada función (presupuesto, cantidades, ids).
- Errores externos capturados en el CLI → mensaje controlado, sin traceback.
- Datos sensibles: ninguno. El catálogo es público; no se guardan datos del cliente.
- Stock, fecha de entrega y delivery se derivan a WhatsApp (el agente no los inventa).
