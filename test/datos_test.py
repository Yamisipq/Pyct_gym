import datos


def test_inicializar_y_cargar_csv(tmp_path):
    ruta = tmp_path / "info" / "miembros.csv"
    datos.inicializar_archivo(str(ruta))
    assert ruta.exists()
    # cargar datos vacíos -> lista vacía
    datos_list = datos.cargar_datos(str(ruta))
    assert isinstance(datos_list, list)
    assert len(datos_list) == 0


def test_guardar_y_cargar_json(tmp_path):
    ruta = tmp_path / "info" / "inscripciones.json"
    datos.inicializar_archivo(str(ruta))
    datos.guardar_datos(str(ruta), [{"id_miembro": "1", "id_clase": "10"}])
    cargado = datos.cargar_datos(str(ruta))
    assert isinstance(cargado, list)
    assert cargado[0]["id_miembro"] == "1"
