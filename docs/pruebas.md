# Matriz de pruebas · Asesor de regalos Aroma

Dos niveles de prueba:

- **A. Lógica de herramientas (offline, reproducible):** `tests/test_herramientas.py`.
  No requiere Azure. Verifica la fuente de verdad y los tres tipos de caso.
- **B. Agente end-to-end (con Foundry):** guion manual para la demo del video.

---

## A. Pruebas automáticas de herramientas (offline)

Ejecuta desde la raíz del repo:

```bash
python tests/test_herramientas.py
```

| # | Caso | Tipo | Entrada | Resultado esperado | Resultado obtenido |
|---|------|------|---------|--------------------|--------------------|
| 1 | Búsqueda por ocasión + presupuesto | Normal | `buscar_productos(ocasion="cervecero", presupuesto_max=100)` | Incluye `box-papa-heroe`; todos ≤ S/100; orden ascendente | ✅ OK |
| 2 | Armar pedido | Normal | Papá Héroe x1 + Luna Serena x2 | Total S/ 125 y enlace `wa.me/51998570380?text=...` | ✅ OK |
| 3 | Solo categoría | Normal | `buscar_productos(categoria="infusiones")` | ≥ 9 resultados | ✅ OK |
| 4 | Presupuesto muy bajo | Límite | `buscar_productos(categoria="boxes", presupuesto_max=10)` | Sin resultados + aviso "el más económico cuesta S/…" | ✅ OK |
| 5 | Producto inexistente en pedido | Fallo | `armar_pedido([{"id":"box-inexistente","cantidad":1}])` | `error` controlado "no existe" | ✅ OK |
| 6 | Pedido vacío | Fallo | `armar_pedido([])` | `error` "pedido está vacío" | ✅ OK |
| 7 | Presupuesto negativo | Fallo | `buscar_productos(presupuesto_max=-5)` | `error` de validación | ✅ OK |

Última ejecución: **7/7 pruebas pasaron.**

---

## B. Pruebas del agente end-to-end (con Foundry)

Requiere `crear_agente.py` ejecutado y `python src/asesor.py` activo.

| # | Caso | Tipo | Pregunta | Qué debe pasar |
|---|------|------|----------|----------------|
| 1 | Recomendación con presupuesto | Normal | "Busco un regalo para mi papá que ama la cerveza, tengo S/100" | Llama `buscar_productos`; recomienda Papá Héroe (S/85) u otro ≤ S/100, con lo que incluye |
| 2 | Pregunta de contenido (RAG) | Normal | "¿Qué trae el box Esencia Eterna?" | Usa File Search y lista los ítems reales del box |
| 3 | Armar pedido | Normal | "Ese me gusta, quiero 1 y 2 frascos de Luna Serena" | Llama `armar_pedido`; da total S/ 125 y enlace de WhatsApp |
| 4 | Fuera de presupuesto | Límite | "Algo para San Valentín por menos de S/40" | Reconoce que no hay boxes tan baratos; ofrece la opción más cercana o una infusión, sin inventar |
| 5 | Fuera de catálogo | Límite | "¿Venden tazas de Star Wars?" | Aclara que no está en el catálogo; no inventa |
| 6 | Entrada inválida / fallo | Fallo | Backend caído o mensaje vacío | Mensaje controlado, sin traceback |

Registra en la demo: pregunta, herramienta activada y respuesta obtenida.
