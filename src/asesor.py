"""
Asesor de regalos Aroma — chat por terminal con memoria y function calling.

Reutiliza el agente publicado (por AGENT_NAME), mantiene una conversación con
memoria (mismo conversation_id) y resuelve el bucle de herramientas: cuando el
modelo pide una función, la ejecutamos localmente y devolvemos el resultado en
una segunda Response, hasta obtener el texto final.

Ejecuta (tras crear_agente.py, con .venv y az login):
    python src/asesor.py           (escribe 'salir' para terminar)

Requiere en .env: PROJECT_ENDPOINT, AGENT_NAME.
"""
import json
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from herramientas import ejecutar_funcion

load_dotenv()

# Cuántas rondas de herramientas permitimos por turno (evita bucles infinitos).
MAX_RONDAS_TOOLS = 5


def _iter_llamadas_funcion(response):
    """Extrae los items de tipo function_call de una Response."""
    for item in getattr(response, "output", None) or []:
        if getattr(item, "type", None) == "function_call":
            yield item


def responder(openai, agent_name, conversation_id, texto_usuario):
    """Envía el mensaje del usuario y resuelve las herramientas hasta la respuesta final."""
    agent_reference = {"name": agent_name, "type": "agent_reference"}

    response = openai.responses.create(
        conversation=conversation_id,
        input=texto_usuario,
        extra_body={"agent_reference": agent_reference},
    )

    for _ in range(MAX_RONDAS_TOOLS):
        llamadas = list(_iter_llamadas_funcion(response))
        if not llamadas:
            break

        # Ejecuta cada función pedida y prepara las salidas.
        salidas = []
        for llamada in llamadas:
            try:
                argumentos = json.loads(llamada.arguments or "{}")
            except json.JSONDecodeError:
                argumentos = {}
            resultado = ejecutar_funcion(llamada.name, argumentos)
            salidas.append(
                {
                    "type": "function_call_output",
                    "call_id": llamada.call_id,
                    "output": resultado,
                }
            )

        # Segunda Response con los resultados de las herramientas.
        response = openai.responses.create(
            conversation=conversation_id,
            input=salidas,
            extra_body={"agent_reference": agent_reference},
        )

    return response.output_text


def main():
    credential = DefaultAzureCredential()
    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=credential,
    )
    openai = project.get_openai_client()
    agent_name = os.environ["AGENT_NAME"]

    conversation = openai.conversations.create()
    print("Asesor de regalos Aroma 🌿  (escribe 'salir' para terminar)\n")

    try:
        while True:
            texto = input("Tú: ").strip()
            if texto.lower() in {"salir", "exit", "quit"}:
                break
            if not texto:
                print("Asesor: Cuéntame para quién buscas el regalo y tu presupuesto. 🙂\n")
                continue
            try:
                respuesta = responder(openai, agent_name, conversation.id, texto)
            except Exception as exc:  # noqa: BLE001 - error controlado hacia el usuario
                print(f"Asesor: Uy, tuve un problema técnico ({exc}). Intenta de nuevo.\n")
                continue
            print(f"Asesor: {respuesta}\n")
    finally:
        openai.conversations.delete(conversation_id=conversation.id)
        openai.close()
        project.close()
        credential.close()


if __name__ == "__main__":
    main()
