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

#----- test de eliminar mienbros

memoria = {"inscripciones": []}

def cargar_datos(filepath):
    return list(memoria["inscripciones"])

def guardar_datos(filepath, lista):
    memoria["inscripciones"] = list(lista)

crud.datos.cargar_datos = cargar_datos
crud.datos.guardar_datos = guardar_datos


def test_eliminar_inscripciones_miembro_elimina_correctamente():
    memoria["inscripciones"] = [
        {"id_miembro": "1", "id_clase": "A"},
        {"id_miembro": "2", "id_clase": "B"},
        {"id_miembro": "1", "id_clase": "C"},
    ]

    resultado = crud.eliminar_inscripciones_miembro("inscripciones", "1")

    assert resultado == 2
    assert memoria["inscripciones"] == [{"id_miembro": "2", "id_clase": "B"}]


def test_eliminar_inscripciones_miembro_sin_coincidencias():
    memoria["inscripciones"] = [
        {"id_miembro": "5", "id_clase": "X"},
        {"id_miembro": "6", "id_clase": "Y"},
    ]

    resultado = crud.eliminar_inscripciones_miembro("inscripciones", "1")

    assert resultado == 0
    assert memoria["inscripciones"] == [
        {"id_miembro": "5", "id_clase": "X"},
        {"id_miembro": "6", "id_clase": "Y"},
    ]


memoria = {
    "miembros": [],
    "inscripciones": []
}

def cargar_datos(filepath):
    if "miembros" in filepath:
        return list(memoria["miembros"])
    elif "inscripciones" in filepath:
        return list(memoria["inscripciones"])
    return []

def guardar_datos(filepath, lista):
    if "miembros" in filepath:
        memoria["miembros"] = list(lista)
    elif "inscripciones" in filepath:
        memoria["inscripciones"] = list(lista)

crud.datos.cargar_datos = cargar_datos
crud.datos.guardar_datos = guardar_datos


def test_eliminar_miembro_con_inscripciones():
    memoria["miembros"] = [
        {"id_miembro": "1", "nombre": "Juan"},
        {"id_miembro": "2", "nombre": "Ana"},
    ]
    memoria["inscripciones"] = [
        {"id_miembro": "1", "id_clase": "A"},
        {"id_miembro": "2", "id_clase": "B"},
        {"id_miembro": "1", "id_clase": "C"},
    ]

    resultado = crud.eliminar_miembro("miembros", "1", "inscripciones")

    assert resultado is True
    assert memoria["miembros"] == [{"id_miembro": "2", "nombre": "Ana"}]
    assert memoria["inscripciones"] == [{"id_miembro": "2", "id_clase": "B"}]


def test_eliminar_miembro_sin_inscripciones():
    memoria["miembros"] = [
        {"id_miembro": "1", "nombre": "Laura"},
        {"id_miembro": "2", "nombre": "Andrés"},
    ]
    memoria["inscripciones"] = []

    resultado = crud.eliminar_miembro("miembros", "2")

    assert resultado is True
    assert memoria["miembros"] == [{"id_miembro": "1", "nombre": "Laura"}]


def test_eliminar_miembro_no_existente():
    memoria["miembros"] = [
        {"id_miembro": "1", "nombre": "Laura"},
        {"id_miembro": "2", "nombre": "Andrés"},
    ]

    resultado = crud.eliminar_miembro("miembros", "99")




