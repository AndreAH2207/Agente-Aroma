# Guion del video · 3:00 exactos

Regla: máximo 3:00. El evaluador debe ver el agente funcionando, una herramienta
o fuente real y un límite gestionado. Muestra la terminal, no diapositivas
interminables.

| Tiempo | Bloque | Qué decir / mostrar |
|--------|--------|---------------------|
| 0:00–0:20 | **Problema** | "Aroma vende infusiones y boxes de regalo. Muchos clientes no saben cuál elegir; hoy eso lo resuelve una persona por WhatsApp. Este agente lo automatiza." (muestra la web de Aroma y su llamado "cuéntanos para quién es"). |
| 0:20–0:45 | **Solución** | Nombre: *Asesor de regalos Aroma*. Entrada: ocasión, destinatario y presupuesto. Salida: recomendación real + pedido por WhatsApp. Límite: no inventa productos ni precios. |
| 0:45–1:10 | **Arquitectura** | Muestra el diagrama de `docs/arquitectura.md`: modelo + instrucciones, File Search (RAG del catálogo) y dos funciones (buscar_productos, armar_pedido). Una sola fuente de verdad. |
| 1:10–2:10 | **Demo** | En terminal: "Regalo para mi papá cervecero, tengo S/100" → recomienda **Papá Héroe (S/85)** (se activa `buscar_productos`). Luego "¿Qué incluye?" (RAG). Luego "Quiero ese y 2 Luna Serena" → **total S/125 + enlace WhatsApp** (`armar_pedido`). |
| 2:10–2:35 | **Prueba límite** | "Algo para San Valentín por menos de S/40" → el agente reconoce que no hay boxes tan baratos y ofrece la opción más cercana, sin inventar. |
| 2:35–2:55 | **Aprendizaje** | Decisión técnica: separar la lógica de las tools para probarla offline (7/7 pruebas). Mejora futura: exponer `/chat` con FastAPI e integrarlo en la web. |
| 2:55–3:00 | **Cierre** | "Repositorio en GitHub. Aroma: regala emoción, ahora con un asesor que nunca se equivoca de precio." |

## Antes de grabar
- `python tests/test_herramientas.py` → 7/7 en pantalla da confianza.
- Ten `python src/asesor.py` ya corriendo para no perder tiempo.
- Ensaya con cronómetro. Audio claro.
