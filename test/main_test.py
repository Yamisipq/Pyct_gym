import os

import pytest
import  main



def test_solicitar_tipo_suscripcion_opcion_mensual(monkeypatch):
    monkeypatch.setattr("main.Prompt.ask", lambda *a, **k: "1")
    assert main.solicitar_tipo_suscripcion() == "Mensual"


def test_solicitar_tipo_suscripcion_opcion_anual(monkeypatch):
    monkeypatch.setattr("main.Prompt.ask", lambda *a, **k: "2")
    assert main.solicitar_tipo_suscripcion() == "Anual"


def test_solicitar_tipo_suscripcion_opcion_vacia(monkeypatch):
    monkeypatch.setattr("main.Prompt.ask", lambda *a, **k: "0")
    assert main.solicitar_tipo_suscripcion(permitir_vacio=True) is None

 # ============================================================
 #   TEST obtener_rutas_archivos
 # =========================================================


def test_obtener_rutas_archivos():
        miembros, clases, inscripciones = main.obtener_rutas_archivos()
        assert "miembros.csv" in miembros
        assert "clases.csv" in clases
        assert "inscripciones.json" in inscripciones

# ============================================================
#   TEST inicializar_directorios
# ============================================================

def test_inicializar_directorios_crea_directorio(tmp_path, monkeypatch):
    ruta = tmp_path / "info"
    monkeypatch.setattr(main, "DIRECTORIO_DATOS", str(ruta))

    main.inicializar_directorios()
    assert os.path.exists(ruta)


def test_inicializar_directorios_no_falla_si_existe(tmp_path, monkeypatch):
    ruta = tmp_path / "info"
    ruta.mkdir()
    monkeypatch.setattr(main, "DIRECTORIO_DATOS", str(ruta))

    main.inicializar_directorios()
    assert ruta.exists()
#----------
#opciones

def test_procesar_opcion_llama_funcion_correcta(monkeypatch):
    llamados = {}

    monkeypatch.setattr(main, "menu_crear_miembro", lambda x: llamados.setdefault("1", True))
    monkeypatch.setattr(main, "menu_leer_miembros", lambda x: llamados.setdefault("2", True))
    monkeypatch.setattr(main, "actz_miembros", lambda x: llamados.setdefault("3", True))
    monkeypatch.setattr(main, "elim_miembro", lambda a, b: llamados.setdefault("4", True))
    monkeypatch.setattr(main, "menu_crear_clase", lambda x: llamados.setdefault("5", True))
    monkeypatch.setattr(main, "menu_leer_clases", lambda x: llamados.setdefault("6", True))
    monkeypatch.setattr(main, "menu_inscribir_miembro", lambda a, b: llamados.setdefault("7", True))
    monkeypatch.setattr(main, "menu_mostrar_miembros_inscritos", lambda a, b: llamados.setdefault("8", True))
    monkeypatch.setattr(main, "baja_miembro", lambda x: llamados.setdefault("9", True))
    monkeypatch.setattr(main, "clases_miembro", lambda a, b: llamados.setdefault("10", True))

    for opcion in map(str, range(1, 11)):
        main.procesar_opcion(opcion, "m", "c", "i")

    assert set(llamados.keys()) == set(str(i) for i in range(1, 11))


def test_procesar_opcion_caso_salida(monkeypatch):
    monkeypatch.setattr(main.console, "print", lambda *a, **k: None)
    resultado = main.procesar_opcion("0", "m", "c", "i")
    assert resultado is False