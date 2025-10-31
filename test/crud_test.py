
import crud
import datos


def setup_paths(tmp_path):
    info = tmp_path / "info"
    miembros = info / "miembros.csv"
    clases = info / "clases.csv"
    inscripciones = info / "inscripciones.json"
    return str(miembros), str(clases), str(inscripciones)


def test_crear_y_leer_miembro(tmp_path):
    path_m, path_c, path_i = setup_paths(tmp_path)
    datos.inicializar_archivo(path_m)
    # Crear miembro
    miembro = crud.crear_miembro(path_m, "Juan Perez", "Mensual")
    assert miembro is not None
    # Leer y verificar
    miembros = crud.leer_todos_los_miembros(path_m)
    assert any(m["nombre"] == "Juan Perez" for m in miembros)


def test_crear_clase_y_leer(tmp_path):
    path_m, path_c, path_i = setup_paths(tmp_path)
    datos.inicializar_archivo(path_c)
    clase = crud.crear_clase(path_c, "Yoga", "Ana", 2)
    assert clase is not None
    clases = crud.leer_todas_las_clases(path_c)
    assert any(c["nombre_clase"] == "Yoga" for c in clases)


def test_inscribir_miembro_en_clase(tmp_path):
    path_m, path_c, path_i = setup_paths(tmp_path)
    datos.inicializar_archivo(path_m)
    datos.inicializar_archivo(path_c)
    datos.inicializar_archivo(path_i)
    miembro = crud.crear_miembro(path_m, "Luisa", "Anual")
    clase = crud.crear_clase(path_c, "Pilates", "Carlos", 1)
    ok, msg = crud.inscribir_miembro_en_clase(path_i, path_c,
        miembro["id_miembro"], clase["id_clase"])
    assert ok is True
    ok2, msg2 = crud.inscribir_miembro_en_clase(path_i, path_c,
        miembro["id_miembro"], clase["id_clase"])
    assert ok2 is False


def test_cupo_maximo(tmp_path):
    path_m, path_c, path_i = setup_paths(tmp_path)
    datos.inicializar_archivo(path_m)
    datos.inicializar_archivo(path_c)
    datos.inicializar_archivo(path_i)
    m1 = crud.crear_miembro(path_m, "A", "Mensual")
    m2 = crud.crear_miembro(path_m, "B", "Mensual")
    clase = crud.crear_clase(path_c, "Box", "Entrenador", 1)
    ok1, _ = crud.inscribir_miembro_en_clase(path_i, path_c, m1["id_miembro"],
        clase["id_clase"])
    assert ok1 is True
    ok2, _ = crud.inscribir_miembro_en_clase(path_i, path_c, m2["id_miembro"],
        clase["id_clase"])
    assert ok2 is False
