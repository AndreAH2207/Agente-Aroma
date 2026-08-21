"""
Pruebas OFFLINE de la lógica de las herramientas del asesor.

No requieren Azure ni red: validan la fuente de verdad (catálogo) y el
comportamiento de buscar_productos / armar_pedido en tres tipos de caso:
normal, límite y fallo. Ejecuta desde la raíz del repo:

    python -m pytest -q            # si tienes pytest
    python tests/test_herramientas.py   # sin pytest (runner incluido abajo)
"""
import sys
from pathlib import Path

# Permite importar los módulos de src/ sin instalar el paquete.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from herramientas import armar_pedido, buscar_productos  # noqa: E402


# ---------------- Casos NORMALES (camino feliz) ----------------
def test_busqueda_por_ocasion_y_presupuesto():
    """Regalo para papá cervecero con S/100: debe traer boxes válidos y baratos primero."""
    r = buscar_productos(ocasion="cervecero", presupuesto_max=100)
    ids = [p["id"] for p in r["resultados"]]
    assert "box-papa-heroe" in ids  # S/85, cabe en el presupuesto
    assert all(p["precio"] <= 100 for p in r["resultados"])
    # Ordenado por precio ascendente.
    precios = [p["precio"] for p in r["resultados"]]
    assert precios == sorted(precios)


def test_armar_pedido_calcula_total_y_enlace():
    """El total y el enlace de WhatsApp deben salir bien formados."""
    r = armar_pedido([
        {"id": "box-papa-heroe", "cantidad": 1},
        {"id": "sabor-luna-serena", "cantidad": 2},
    ])
    assert r["total"] == 85 + 20 * 2  # 125
    assert r["total_texto"] == "S/ 125"
    assert r["enlace_whatsapp"].startswith("https://wa.me/51998570380?text=")


# ---------------- Casos LÍMITE ----------------
def test_presupuesto_demasiado_bajo_no_inventa():
    """Con S/10 no hay nada: debe avisar y NO devolver productos."""
    r = buscar_productos(categoria="boxes", presupuesto_max=10)
    assert r["resultados"] == []
    assert "más económico" in r["mensaje"]


def test_categoria_sin_ocasion_devuelve_algo():
    """Filtro amplio (solo categoría) debe devolver resultados."""
    r = buscar_productos(categoria="infusiones")
    assert r["total_encontrados"] >= 9


# ---------------- Casos de FALLO / entrada inválida ----------------
def test_producto_inexistente_en_pedido():
    """Un id que no existe debe producir un error controlado, no un crash."""
    r = armar_pedido([{"id": "box-inexistente", "cantidad": 1}])
    assert "error" in r
    assert "no existe" in r["error"]


def test_pedido_vacio():
    r = armar_pedido([])
    assert "error" in r


def test_presupuesto_negativo():
    r = buscar_productos(presupuesto_max=-5)
    assert "error" in r


# ---------------- Runner mínimo sin pytest ----------------
if __name__ == "__main__":
    pruebas = [obj for nombre, obj in sorted(globals().items()) if nombre.startswith("test_")]
    fallos = 0
    for prueba in pruebas:
        try:
            prueba()
            print(f"  OK   {prueba.__name__}")
        except AssertionError as exc:
            fallos += 1
            print(f"  FALLA {prueba.__name__}: {exc}")
    total = len(pruebas)
    print(f"\n{total - fallos}/{total} pruebas pasaron.")
    sys.exit(1 if fallos else 0)
