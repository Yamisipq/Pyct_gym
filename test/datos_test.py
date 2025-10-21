
import pytest
import json
import csv
import os
import datos


def test_inicializar_archivo_csv(tmp_path):
    ruta = tmp_path / "miembros.csv"
    datos.inicializar_archivo(str(ruta))
    assert ruta.exists()
    with open(ruta, "r", encoding="utf-8") as f:
        cabecera = f.readline().strip().split(",")
    assert "id_miembro" in cabecera
    assert "nombre" in cabecera


def test_inicializar_archivo_json(tmp_path):
    ruta = tmp_path / "inscripciones.json"
    datos.inicializar_archivo(str(ruta))
    assert ruta.exists()
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = json.load(f)
    assert contenido == []


def test_guardar_y_cargar_csv(tmp_path):
    ruta = tmp_path / "miembros.csv"
    datos.inicializar_archivo(str(ruta))
    data = [{"id_miembro": "1", "nombre": "Carlos", "tipo_suscripcion": "Mensual"}]
    datos.guardar_datos(str(ruta), data)
    cargado = datos.cargar_datos(str(ruta))
    assert cargado == data


def test_guardar_y_cargar_json(tmp_path):
    ruta = tmp_path / "inscripciones.json"
    data = [{"id_miembro": "1", "id_clase": "10"}]
    datos.guardar_datos(str(ruta), data)
    cargado = datos.cargar_datos(str(ruta))
    assert cargado == data
