import pytest  # noqa: F401

import crud
import datos


def crear_miembro(filepath, nombre, tipo_suscripcion):
    datos.inicializar_archivo(filepath)

def leer_miembro(tmp_path):
    path = tmp_path / "info/miembros.csv"

    miembros = crud.leer_todos_los_miembros(str(path))
    assert len(miembros) == 1
    assert miembros[0]["nombre"] == "Carlos"


def test_buscar_y_actualizar_miembro(tmp_path):
    path = tmp_path / "info/miembros.csv"
    m1 = crud.crear_miembro(str(path), "Laura", "Anual")

    buscado = crud.buscar_miembro_por_id(str(path), m1["id_miembro"])
    assert buscado["nombre"] == "Laura"

    actualizado = crud.actualizar_miembro(str(path),
        m1["id_miembro"], {"nombre": "Laura Actualizada"})
    assert actualizado["nombre"] == "Laura Actualizada"

    miembros = crud.leer_todos_los_miembros(str(path))
    assert miembros[0]["nombre"] == "Laura Actualizada"


def test_eliminar_miembro(tmp_path):
    path = tmp_path / "info/miembros.csv"
    m1 = crud.crear_miembro(str(path), "Mario", "Mensual")

    exito = crud.eliminar_miembro(str(path), m1["id_miembro"])
    assert exito is True

    miembros = crud.leer_todos_los_miembros(str(path))
    assert len(miembros) == 1
    assert miembros[0]["nombre"] == "Ana"

