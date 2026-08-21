"""
Herramientas (function tools) del Asesor de regalos Aroma.

Contiene DOS cosas separadas a propósito:

1. La lógica pura en Python (buscar_productos / armar_pedido). No depende de
   Azure ni de la red, así que se puede probar localmente y de forma
   reproducible (ver tests/test_herramientas.py).

2. Los esquemas JSON (FUNCTION_SCHEMAS) que se declaran al agente y el
   despachador (ejecutar_funcion) que conecta el nombre de la función que
   pide el modelo con la implementación real.

Validación: cada función revisa sus entradas y devuelve un mensaje de error
controlado en vez de lanzar excepciones hacia el modelo.
"""
from __future__ import annotations

import json
from urllib.parse import quote

from catalogo import cargar_catalogo, formato_precio, productos

# Presupuesto mínimo razonable: el producto más barato del catálogo.
_PRECIO_MINIMO_CATALOGO = 29


# --------------------------------------------------------------------------
# Herramienta 1: buscar_productos
# --------------------------------------------------------------------------
def buscar_productos(
    ocasion: str | None = None,
    categoria: str | None = None,
    presupuesto_max: float | None = None,
    presupuesto_min: float | None = None,
    limite: int = 5,
) -> dict:
    """Filtra el catálogo real por ocasión, categoría y rango de precio.

    Devuelve un dict con la lista de coincidencias (ordenadas por precio) o un
    aviso claro cuando no hay resultados dentro del presupuesto. Nunca inventa
    productos: solo devuelve lo que existe en el catálogo.
    """
    # Validación de presupuesto.
    if presupuesto_max is not None:
        try:
            presupuesto_max = float(presupuesto_max)
        except (TypeError, ValueError):
            return {"error": "El presupuesto máximo debe ser un número en soles."}
        if presupuesto_max <= 0:
            return {"error": "El presupuesto máximo debe ser mayor que 0."}

    if presupuesto_min is not None:
        try:
            presupuesto_min = float(presupuesto_min)
        except (TypeError, ValueError):
            return {"error": "El presupuesto mínimo debe ser un número en soles."}

    items = productos()

    if categoria:
        cat = categoria.strip().lower()
        items = [p for p in items if p["categoria"] == cat]

    if ocasion:
        occ = ocasion.strip().lower()
        items = [p for p in items if occ in p.get("ocasiones", []) or occ in p.get("perfil", [])]

    if presupuesto_min is not None:
        items = [p for p in items if p["precio"] >= presupuesto_min]

    dentro_de_presupuesto = items
    if presupuesto_max is not None:
        dentro_de_presupuesto = [p for p in items if p["precio"] <= presupuesto_max]

    # Caso límite: hay productos pero ninguno entra en el presupuesto.
    if presupuesto_max is not None and not dentro_de_presupuesto:
        mas_barato = min((p["precio"] for p in productos()), default=_PRECIO_MINIMO_CATALOGO)
        return {
            "resultados": [],
            "mensaje": (
                f"No hay productos con esos filtros por debajo de "
                f"{formato_precio(presupuesto_max)}. El producto más económico "
                f"del catálogo cuesta {formato_precio(mas_barato)}."
            ),
        }

    ordenados = sorted(dentro_de_presupuesto, key=lambda p: p["precio"])
    recorte = ordenados[: max(1, int(limite))]

    return {
        "total_encontrados": len(ordenados),
        "resultados": [
            {
                "id": p["id"],
                "nombre": p["nombre"],
                "categoria": p["categoria"],
                "precio": p["precio"],
                "precio_texto": formato_precio(p["precio"]),
                "descripcion": p["descripcion"],
                "incluye": p.get("incluye", []),
            }
            for p in recorte
        ],
    }


# --------------------------------------------------------------------------
# Herramienta 2: armar_pedido
# --------------------------------------------------------------------------
def armar_pedido(items: list[dict]) -> dict:
    """Calcula el total y genera el enlace de WhatsApp del pedido.

    `items` es una lista de {"id": str, "cantidad": int}. El formato del
    mensaje replica exactamente el checkout de la web de Aroma para que el
    pedido llegue igual que desde el carrito.
    """
    if not items:
        return {"error": "El pedido está vacío. Agrega al menos un producto."}

    catalogo = cargar_catalogo()
    lineas_texto = []
    detalle = []
    total = 0.0

    for item in items:
        pid = (item or {}).get("id")
        cantidad = (item or {}).get("cantidad", 1)
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            return {"error": f"Cantidad inválida para '{pid}'."}
        if cantidad <= 0:
            return {"error": f"La cantidad de '{pid}' debe ser mayor que 0."}

        producto = next((p for p in catalogo["productos"] if p["id"] == pid), None)
        if producto is None:
            return {
                "error": (
                    f"El producto '{pid}' no existe en el catálogo. "
                    "Usa buscar_productos para obtener ids válidos."
                )
            }

        subtotal = producto["precio"] * cantidad
        total += subtotal
        detalle.append(
            {
                "id": pid,
                "nombre": producto["nombre"],
                "cantidad": cantidad,
                "subtotal": subtotal,
                "subtotal_texto": formato_precio(subtotal),
            }
        )
        lineas_texto.append(f"▪ {cantidad} x {producto['nombre']} — {formato_precio(subtotal)}")

    mensaje = "\n".join(
        [
            "¡Hola Aroma! 🌿 Quiero hacer este pedido:",
            "",
            *lineas_texto,
            "",
            f"*Total: {formato_precio(total)}*",
            "",
            "Mi distrito de entrega es: ",
        ]
    )

    numero = catalogo.get("whatsapp", "")
    enlace = f"https://wa.me/{numero}?text={quote(mensaje)}"

    return {
        "detalle": detalle,
        "total": total,
        "total_texto": formato_precio(total),
        "nota": "El delivery se coordina por WhatsApp según el distrito.",
        "enlace_whatsapp": enlace,
    }


# --------------------------------------------------------------------------
# Declaración de herramientas para el agente (JSON Schema)
# --------------------------------------------------------------------------
FUNCTION_SCHEMAS = [
    {
        "name": "buscar_productos",
        "description": (
            "Busca productos reales del catálogo de Aroma filtrando por ocasión, "
            "categoría y presupuesto. Úsala siempre antes de recomendar, para no "
            "inventar productos ni precios."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "ocasion": {
                    "type": "string",
                    "description": (
                        "Ocasión o perfil: dia-del-padre, dia-de-la-madre, san-valentin, "
                        "aniversario, cumpleanos, pascua, personal, relajacion, familia, "
                        "complemento, cervecero, vino."
                    ),
                },
                "categoria": {
                    "type": "string",
                    "enum": ["infusiones", "promos", "boxes", "romanticos", "pascua", "accesorios"],
                    "description": "Categoría del producto.",
                },
                "presupuesto_max": {
                    "type": "number",
                    "description": "Precio máximo en soles (S/).",
                },
                "presupuesto_min": {
                    "type": "number",
                    "description": "Precio mínimo en soles (S/).",
                },
                "limite": {
                    "type": "integer",
                    "description": "Máximo de resultados a devolver (por defecto 5).",
                },
            },
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "name": "armar_pedido",
        "description": (
            "Calcula el total de un pedido y genera el enlace de WhatsApp listo "
            "para enviar. Úsala cuando el cliente ya eligió qué llevar."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "description": "Productos del pedido.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "id exacto del producto."},
                            "cantidad": {"type": "integer", "description": "Cantidad (>=1)."},
                        },
                        "required": ["id", "cantidad"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["items"],
            "additionalProperties": False,
        },
    },
]

# Mapa nombre -> implementación, usado por el despachador.
_IMPLEMENTACIONES = {
    "buscar_productos": buscar_productos,
    "armar_pedido": armar_pedido,
}


def ejecutar_funcion(nombre: str, argumentos: dict) -> str:
    """Ejecuta la función pedida por el modelo y devuelve su salida como JSON.

    Si el nombre no existe o los argumentos son inválidos, devuelve un JSON de
    error controlado (nunca lanza hacia el modelo).
    """
    funcion = _IMPLEMENTACIONES.get(nombre)
    if funcion is None:
        return json.dumps({"error": f"Función desconocida: {nombre}"}, ensure_ascii=False)
    try:
        resultado = funcion(**(argumentos or {}))
    except TypeError as exc:
        resultado = {"error": f"Argumentos inválidos para {nombre}: {exc}"}
    return json.dumps(resultado, ensure_ascii=False)
