# Asesor de regalos Aroma 🌿

Agente conversacional que ayuda a los clientes de **Aroma** (infusiones
artesanales y boxes de regalo, Perú) a elegir el regalo ideal según ocasión,
destinatario y presupuesto — y arma el pedido con el enlace de WhatsApp listo
para enviar.

Trabajo final del microprograma *Agentes de IA con Microsoft Foundry + Python*.
Construido con `azure-ai-projects` 2.4.0 (API v1): agente versionado, File Search
(RAG) y function calling.

## Qué hace

- **Recomienda** productos reales del catálogo por ocasión y presupuesto (función `buscar_productos`).
- **Responde** qué incluye cada box, ingredientes y cómo comprar, citando el catálogo (File Search / RAG).
- **Arma el pedido**: calcula el total y genera el enlace de WhatsApp con el mismo formato del carrito de la web (función `armar_pedido`).
- **Declara sus límites**: no inventa productos ni precios; stock, entrega y delivery se confirman por WhatsApp.

## Arquitectura

`Cliente → asesor.py → Responses API → Agente asesor-aroma → (File Search RAG | funciones locales) → recomendación + total + enlace WhatsApp`

Detalle en [docs/arquitectura.md](docs/arquitectura.md).

## Estructura

```
aroma-agente/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── src/
│   ├── catalogo.py        # carga del catálogo (fuente de verdad)
│   ├── herramientas.py    # buscar_productos + armar_pedido (lógica pura + schemas)
│   ├── crear_agente.py    # publica la versión del agente (RAG + tools)
│   └── asesor.py          # CLI conversacional con bucle de function calling
├── data/
│   ├── catalogo-aroma.md   # documento para File Search (RAG)
│   └── catalogo-aroma.json # datos estructurados para las funciones
├── tests/
│   └── test_herramientas.py  # pruebas offline (normal / límite / fallo)
└── docs/
    ├── arquitectura.md
    ├── pruebas.md
    └── ficha.md
```

## Requisitos previos

- Python 3.9+ y Azure CLI.
- Un proyecto de Microsoft Foundry con un modelo desplegado.
- Permisos para usar el proyecto (rol adecuado sobre el recurso de Foundry).

## Instalación (desde un entorno limpio)

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
az login
```

Completa `.env` con tus valores:

```
PROJECT_ENDPOINT=https://tu-recurso.services.ai.azure.com/api/projects/tu-proyecto
MODEL_DEPLOYMENT_NAME=tu-deployment
AGENT_NAME=asesor-aroma
```

## Uso

1. **Publica el agente** (una sola vez, o cuando cambies instrucciones/catálogo):

   ```bash
   python src/crear_agente.py
   ```

   Indexa `data/catalogo-aroma.md`, declara las funciones y crea la versión del agente.

2. **Conversa** con el asesor:

   ```bash
   python src/asesor.py
   ```

   Ejemplo:

   ```
   Tú: Busco un regalo para mi papá que ama la cerveza, tengo S/100
   Asesor: Te recomiendo el box "Papá Héroe" (S/ 85): copa cervecera grabada,
           cerveza artesanal Candelaria, cabanossi, Ferrero Rocher y un frasco
           de infusión Aroma. ¿Quieres que arme el pedido?
   ```

## Pruebas

La lógica de las herramientas se prueba **sin Azure** (reproducible):

```bash
python tests/test_herramientas.py
# o, si tienes pytest:
python -m pytest -q
```

Cubre casos normal, límite (fuera de presupuesto) y fallo (id inexistente,
pedido vacío, presupuesto negativo). Matriz completa y pruebas del agente
end-to-end en [docs/pruebas.md](docs/pruebas.md).

## Seguridad y costos

- Nunca subas `.env` ni credenciales (ya está en `.gitignore`).
- El catálogo es información pública; el agente no guarda datos del cliente.
- En producción: autenticación propia, identidad administrada, límites de tamaño
  y rate limit, y borrar vector stores y agentes de prueba al terminar.

## Datos y atribución

Catálogo, textos e imágenes de productos pertenecen a Aroma · Infusiones
Artesanales. El código de este agente se publica bajo licencia MIT (ver `LICENSE`).
