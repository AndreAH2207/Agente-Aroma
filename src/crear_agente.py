"""
Publica (una sola vez, o cuando cambie la definición) la versión del agente
"Asesor de regalos Aroma" en Microsoft Foundry.

Hace tres cosas:
  1. Crea un vector store e indexa el catálogo (data/catalogo-aroma.md) para RAG.
  2. Declara las dos function tools (buscar_productos, armar_pedido).
  3. Crea una versión del agente con instrucciones de sistema, File Search y funciones.

Ejecuta (con .venv activado y az login hecho):
    python src/crear_agente.py

Requiere en .env: PROJECT_ENDPOINT, MODEL_DEPLOYMENT_NAME, AGENT_NAME.
SDK verificado: azure-ai-projects 2.4.0 (API v1).
"""
import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, FunctionTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from herramientas import FUNCTION_SCHEMAS

load_dotenv()

CATALOGO_MD = Path(__file__).resolve().parent.parent / "data" / "catalogo-aroma.md"

INSTRUCCIONES = (
    "Eres el asesor de regalos de Aroma, una marca peruana de infusiones "
    "artesanales y boxes de regalo. Tu objetivo es ayudar a la persona a elegir "
    "el regalo ideal según para quién es, la ocasión y su presupuesto en soles (S/).\n"
    "\n"
    "Reglas:\n"
    "1. Recomienda SOLO productos reales del catálogo. Para conocerlos usa la "
    "   herramienta buscar_productos; nunca inventes productos, precios ni fechas.\n"
    "2. En cuanto tengas al menos UNO de estos datos —ocasión, destinatario o "
    "   presupuesto— llama de inmediato a buscar_productos. NO narres que vas a "
    "   buscar, no digas 'estoy buscando' ni 'espera un momento': simplemente usa "
    "   la herramienta y responde con los resultados que devuelve.\n"
    "3. Presenta 2 o 3 opciones concretas, cada una con nombre, precio (S/) y qué "
    "   incluye. Sé breve y cálido. No repitas frases.\n"
    "4. Si el cliente da un presupuesto, respétalo. Si nada entra en ese "
    "   presupuesto, dilo con claridad y ofrece la opción más cercana.\n"
    "5. Haz como máximo UNA pregunta, y solo si te falta un dato esencial para "
    "   buscar. Si ya puedes buscar, busca antes de preguntar.\n"
    "6. Para dudas sobre qué incluye un box, ingredientes o cómo comprar, apóyate "
    "   en el documento del catálogo (File Search) y cita el dato.\n"
    "7. Cuando el cliente decida qué llevar, usa armar_pedido para calcular el "
    "   total y entregar el enlace de WhatsApp.\n"
    "8. El stock, la fecha exacta de entrega y el costo de delivery se confirman "
    "   por WhatsApp: indícalo cuando corresponda, no lo inventes."
)


def main():
    credential = DefaultAzureCredential()
    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=credential,
    )
    openai = project.get_openai_client()

    # 1) Vector store con el catálogo para RAG.
    vector_store = openai.vector_stores.create(name="vs-catalogo-aroma")
    with CATALOGO_MD.open("rb") as archivo:
        carga = openai.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=archivo,
        )
    if getattr(carga, "status", None) == "failed":
        raise RuntimeError("Foundry no pudo indexar el catálogo.")
    print(f"Vector store listo: {vector_store.id}")

    # 2) Herramientas: File Search (RAG) + funciones.
    file_search = FileSearchTool(vector_store_ids=[vector_store.id])
    funciones = [FunctionTool(**schema) for schema in FUNCTION_SCHEMAS]

    # 3) Crear la versión del agente.
    agent = project.agents.create_version(
        agent_name=os.environ["AGENT_NAME"],
        definition=PromptAgentDefinition(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            instructions=INSTRUCCIONES,
            tools=[file_search, *funciones],
        ),
    )

    print("=" * 52)
    print(f"  Agente publicado: {agent.name} (versión {agent.version})")
    print("  Guarda el vector store si quieres reutilizarlo.")
    print("  Conversa con:  python src/asesor.py")
    print("=" * 52)

    openai.close()
    project.close()
    credential.close()


if __name__ == "__main__":
    main()
