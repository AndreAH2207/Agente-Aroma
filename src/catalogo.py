"""
Carga del catálogo de Aroma (fuente de verdad para las herramientas).

El catálogo vive en data/catalogo-aroma.json y es el mismo contenido que el
documento indexado para RAG. Mantener una sola fuente evita que el agente
recomiende productos o precios que no existen.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

# data/ está junto a src/, un nivel por encima de este archivo.
CATALOGO_PATH = Path(__file__).resolve().parent.parent / "data" / "catalogo-aroma.json"


@lru_cache(maxsize=1)
def cargar_catalogo() -> dict:
    """Lee y cachea el catálogo completo desde el JSON."""
    with CATALOGO_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def productos() -> list[dict]:
    """Devuelve la lista de productos."""
    return cargar_catalogo()["productos"]


def buscar_por_id(product_id: str) -> dict | None:
    """Busca un producto por su id exacto; None si no existe."""
    return next((p for p in productos() if p["id"] == product_id), None)


def categorias_validas() -> set[str]:
    """Conjunto de categorías presentes en el catálogo."""
    return {p["categoria"] for p in productos()}


def formato_precio(valor: float) -> str:
    """Formatea un monto como la web: 'S/ 59' o 'S/ 59.50'."""
    simbolo = cargar_catalogo().get("simbolo", "S/")
    if valor == int(valor):
        return f"{simbolo} {int(valor)}"
    return f"{simbolo} {valor:.2f}"
