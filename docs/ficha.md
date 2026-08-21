# Ficha breve · Asesor de regalos Aroma

- **Nombre:** Asesor de regalos Aroma 🌿
- **Usuario objetivo:** cliente de Aroma que no sabe qué regalar (por ocasión,
  destinatario o presupuesto) y hoy tendría que preguntar a mano por WhatsApp.
- **Problema:** la web ya invita a "cuéntanos para quién es y te ayudamos a
  elegir", pero ese asesoramiento depende de una persona. El agente lo automatiza.
- **Promesa (fórmula):** para un *cliente indeciso*, el agente ayuda a *elegir el
  regalo ideal* usando *el catálogo real (RAG) y funciones de búsqueda/pedido*,
  entrega *una recomendación con precio y el pedido listo por WhatsApp* y evita
  *inventar productos, precios o fechas de entrega*.

- **Entradas:** ocasión, destinatario y/o presupuesto (texto conversacional).
- **Salidas:** recomendación de productos reales con precio y contenido; total del
  pedido y enlace de WhatsApp listo para enviar.

- **Herramientas:**
  - File Search (RAG) sobre `catalogo-aroma.md` — contenido de boxes, ingredientes, FAQ.
  - `buscar_productos()` — filtra por ocasión, categoría y presupuesto.
  - `armar_pedido()` — calcula total y genera el enlace de WhatsApp.

- **Límites declarados:** solo recomienda del catálogo; respeta el presupuesto;
  stock, fecha de entrega y costo de delivery se confirman por WhatsApp.

- **Riesgos y mitigaciones:**
  - *Recomendar algo inexistente* → las funciones son la única fuente de ids/precios.
  - *Prometer entregas* → el agente deriva a WhatsApp; no confirma fechas.
  - *Entradas inválidas* → validación en las funciones y manejo de error en el CLI.

- **No-objetivos:** no cobra ni procesa pagos, no confirma stock en tiempo real,
  no gestiona el delivery. Cierra el flujo derivando a WhatsApp.

- **Siguientes pasos:** exponer `/chat` con FastAPI e integrarlo como widget en la
  web de Aroma; conectar stock real; añadir seguimiento de campañas de temporada.
