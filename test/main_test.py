import os

import main

# ============================================================
#   HELPERS (mock functions para reemplazar lambdas)
# ============================================================

def fake_prompt_1(*args, **kwargs):
    return "1"

def fake_prompt_2(*args, **kwargs):
    return "2"

def fake_prompt_0(*args, **kwargs):
    return "0"

def fake_print(*args, **kwargs):
    """Evita que Rich imprima en consola durante los tests."""
    pass

def fake_func(registro, valor):
    """Registra la llamada en un diccionario."""
    def inner(*args, **kwargs):
        registro.setdefault(valor, True)
    return inner

# ============================================================
#   TEST solicitar_tipo_suscripcion
# ============================================================

def test_solicitar_tipo_suscripcion_opcion_mensual(monkeypatch):
    monkeypatch.setattr("main.Prompt.ask", fake_prompt_1)
    assert main.solicitar_tipo_suscripcion() == "Mensual"


def test_solicitar_tipo_suscripcion_opcion_anual(monkeypatch):
    monkeypatch.setattr("main.Prompt.ask", fake_prompt_2)
    assert main.solicitar_tipo_suscripcion() == "Anual"


def test_solicitar_tipo_suscripcion_opcion_vacia(monkeypatch):
    monkeypatch.setattr("main.Prompt.ask", fake_prompt_0)
    assert main.solicitar_tipo_suscripcion(permitir_vacio=True) is None

# ============================================================
#   TEST obtener_rutas_archivos
# ============================================================

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

# ============================================================
#   TEST procesar_opcion
# ============================================================

def test_procesar_opcion_llama_funcion_correcta(monkeypatch):
    llamados = {}

    monkeypatch.setattr(main, "menu_crear_miembro", fake_func(llamados, "1"))
    monkeypatch.setattr(main, "menu_leer_miembros", fake_func(llamados, "2"))
    monkeypatch.setattr(main, "actz_miembros", fake_func(llamados, "3"))
    monkeypatch.setattr(main, "elim_miembro", fake_func(llamados, "4"))
    monkeypatch.setattr(main, "menu_crear_clase", fake_func(llamados, "5"))
    monkeypatch.setattr(main, "menu_leer_clases", fake_func(llamados, "6"))
    monkeypatch.setattr(main, "menu_inscribir_miembro", fake_func(llamados, "7"))
    monkeypatch.setattr(main,
        "menu_mostrar_miembros_inscritos", fake_func(llamados, "8"))
    monkeypatch.setattr(main, "baja_miembro", fake_func(llamados, "9"))
    monkeypatch.setattr(main, "clases_miembro", fake_func(llamados, "10"))

    for opcion in map(str, range(1, 11)):
        main.procesar_opcion(opcion, "m", "c", "i")

    assert set(llamados.keys()) == set(str(i) for i in range(1, 11))


def test_procesar_opcion_caso_salida(monkeypatch):
    monkeypatch.setattr(main.console, "print", fake_print)
    resultado = main.procesar_opcion("0", "m", "c", "i")
    assert resultado is False
