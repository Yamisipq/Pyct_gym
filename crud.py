# -*- coding: utf-8 -*-
"""
Módulo de Lógica de Negocio.

Contiene todas las funciones para gestionar el gimnasio (CRUD de Miembros y Clases,
y gestión de Inscripciones).
"""

import csv
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.table import Table

import datos

console = Console()

INFO_DIR = "info"
CLASES_FILE = os.path.join(INFO_DIR, "clases.csv")
INSCRIPCIONES_FILE = os.path.join(INFO_DIR, "inscripciones.json")

VALID_TIPOS_SUSCRIPCION = ("Mensual", "Anual")


def generar_nuevo_id(entidad: str, lista: List[Dict[str, Any]]) -> str:
    """
    Genera un nuevo ID autoincremental para Miembros o Clases.
    """
    id_key = "id_miembro" if entidad == "miembro" else "id_clase"

    if not lista:
        return "1"

    max_id = 0
    for item in lista:
        try:
            current_id = int(item.get(id_key, 0))
            max_id = max(max_id, current_id)
        except ValueError:
            pass

    return str(max_id + 1)


def crear_miembro(
    filepath: str, nombre: str, tipo_suscripcion: str
) -> Optional[Dict[str, Any]]:
    """
    (CREATE) Agrega un nuevo miembro.
    """
    miembros = datos.cargar_datos(filepath)

    if not nombre.strip():
        console.print("[red]El nombre del miembro no puede estar vacío.[/red]")
        return None

    if tipo_suscripcion not in VALID_TIPOS_SUSCRIPCION:
        console.print(f"[red]Tipo de suscripción inválido: {tipo_suscripcion}[/red]")
        return None

    nuevo_id = generar_nuevo_id("miembro", miembros)

    nuevo_miembro = {
        "id_miembro": nuevo_id,
        "nombre": nombre.strip(),
        "tipo_suscripcion": tipo_suscripcion,
    }

    miembros.append(nuevo_miembro)
    datos.guardar_datos(filepath, miembros)
    return nuevo_miembro


def leer_todos_los_miembros(filepath: str) -> List[Dict[str, Any]]:
    """(READ) Obtiene la lista completa de miembros."""
    return datos.cargar_datos(filepath)


def buscar_miembro_por_id(filepath: str, id_miembro: str) -> Optional[Dict[str, Any]]:
    """Busca un miembro específico por su ID."""
    miembros = datos.cargar_datos(filepath)
    for miembro in miembros:
        if miembro.get("id_miembro") == id_miembro:
            return miembro
    return None


def actualizar_miembro(
    filepath: str, id_miembro: str, datos_nuevos: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """(UPDATE) Modifica los datos de un miembro existente."""
    miembros = datos.cargar_datos(filepath)

    for i, miembro in enumerate(miembros):
        if miembro.get("id_miembro") == id_miembro:
            if "tipo_suscripcion" in datos_nuevos:
                tipo = datos_nuevos["tipo_suscripcion"]
                if tipo not in VALID_TIPOS_SUSCRIPCION:
                    console.print(f"[red]Tipo de suscripción inválido: {tipo}[/red]")
                    return None

            miembro.update(datos_nuevos)
            miembros[i] = {k: miembro.get(k, "") for k in datos.CAMPOS_MIEMBROS}
            datos.guardar_datos(filepath, miembros)
            return miembros[i]

    return None


def eliminar_miembro(
    filepath_miembros: str,
    id_miembro: str,
    filepath_inscripciones: str = INSCRIPCIONES_FILE,
) -> bool:
    """(DELETE) Elimina un miembro y todas sus inscripciones asociadas."""
    miembros = datos.cargar_datos(filepath_miembros)
    miembros_iniciales = len(miembros)
    miembros = [m for m in miembros if m.get("id_miembro") != id_miembro]

    if len(miembros) < miembros_iniciales:
        datos.guardar_datos(filepath_miembros, miembros)

        # Eliminar sus inscripciones
        if os.path.exists(filepath_inscripciones):
            inscripciones = datos.cargar_datos(filepath_inscripciones)
            inscripciones = [
                i for i in inscripciones if i.get("id_miembro") != id_miembro
            ]
            datos.guardar_datos(filepath_inscripciones, inscripciones)

        return True

    return False


def crear_clase(
    filepath: str, nombre_clase: str, instructor: str, cupo_maximo: int
) -> Optional[Dict[str, Any]]:
    """(CREATE) Agrega una nueva clase."""
    clases = datos.cargar_datos(filepath)

    if not nombre_clase.strip() or not instructor.strip():
        console.print(
            "[red]El nombre de la clase y el instructor son obligatorios.[/red]"
        )
        return None

    if not isinstance(cupo_maximo, int) or cupo_maximo <= 0:
        console.print("[red]El cupo máximo debe ser un número positivo.[/red]")
        return None

    nuevo_id = generar_nuevo_id("clase", clases)
    nueva_clase = {
        "id_clase": nuevo_id,
        "nombre_clase": nombre_clase.strip(),
        "instructor": instructor.strip(),
        "cupo_maximo": str(cupo_maximo),
    }

    clases.append(nueva_clase)
    datos.guardar_datos(filepath, clases)
    return nueva_clase


def leer_todas_las_clases(filepath: str) -> List[Dict[str, Any]]:
    """(READ) Obtiene la lista completa de clases."""
    return datos.cargar_datos(filepath)


def buscar_clase_por_id(filepath: str, id_clase: str) -> Optional[Dict[str, Any]]:
    """Busca una clase específica por su ID."""
    clases = datos.cargar_datos(filepath)
    for clase in clases:
        if clase.get("id_clase") == id_clase:
            return clase
    return None


def inscribir_miembro_en_clase(
    filepath_inscripciones: str, filepath_clases: str, id_miembro: str, id_clase: str
) -> Tuple[bool, str]:
    """Inscribe a un miembro en una clase."""
    inscripciones = datos.cargar_datos(filepath_inscripciones)
    clase = buscar_clase_por_id(filepath_clases, id_clase)

    if not clase:
        return False, f"Error: Clase con ID '{id_clase}' no encontrada."

    inscritos_clase = [i for i in inscripciones if i["id_clase"] == id_clase]

    if any(i["id_miembro"] == id_miembro for i in inscritos_clase):
        return (
            False,
            f"Error: El miembro '{id_miembro}' ya está inscrito en "
            f"'{clase['nombre_clase']}'.",
        )

    cupo_maximo = int(clase.get("cupo_maximo", 0))
    if len(inscritos_clase) >= cupo_maximo:
        return (
            False,
            f"Error: La clase '{clase['nombre_clase']}' "
            f"alcanzó su cupo máximo ({cupo_maximo}).",
        )

    nueva_inscripcion = {"id_miembro": id_miembro, "id_clase": id_clase}
    inscripciones.append(nueva_inscripcion)
    datos.guardar_datos(filepath_inscripciones, inscripciones)
    return (
        True,
        f"¡Inscripción exitosa! Miembro {id_miembro} en clase {clase['nombre_clase']}.",
    )


def dar_baja_miembro_de_clase(filepath: str, id_miembro: str, id_clase: str) -> bool:
    """Da de baja a un miembro de una clase."""
    inscripciones = datos.cargar_datos(filepath)
    inscripciones_iniciales = len(inscripciones)
    inscripciones = [
        i
        for i in inscripciones
        if not (i.get("id_miembro") == id_miembro and i.get("id_clase") == id_clase)
    ]

    if len(inscripciones) < inscripciones_iniciales:
        datos.guardar_datos(filepath, inscripciones)
        return True
    return False


def listar_miembros_inscritos_en_clase(
    filepath_inscripciones: str, filepath_miembros: str, id_clase: str
) -> List[Dict[str, Any]]:
    """Lista los miembros inscritos en una clase específica."""
    inscripciones = datos.cargar_datos(filepath_inscripciones)
    miembros_todos = datos.cargar_datos(filepath_miembros)
    ids_inscritos = [
        i["id_miembro"] for i in inscripciones if i["id_clase"] == id_clase
    ]
    return [m for m in miembros_todos if m.get("id_miembro") in ids_inscritos]


def listar_clases_inscritas_por_miembro(
    filepath_inscripciones: str, filepath_clases: str, id_miembro: str
) -> List[Dict[str, Any]]:
    """Lista todas las clases en las que está inscrito un miembro."""
    inscripciones = datos.cargar_datos(filepath_inscripciones)
    clases_todas = datos.cargar_datos(filepath_clases)
    ids_clases = [i["id_clase"] for i in inscripciones if i["id_miembro"] == id_miembro]
    return [c for c in clases_todas if c.get("id_clase") in ids_clases]


def ver_cupos_disponibles():
    """Muestra los cupos disponibles por clase."""
    if not os.path.exists(CLASES_FILE):
        console.print("[red]El archivo de clases no existe.[/red]")
        return

    if not os.path.exists(INSCRIPCIONES_FILE):
        console.print("[red]El archivo de inscripciones no existe.[/red]")
        return

    clases = []
    c_column=4
    with open(CLASES_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for fila in reader:
            if not fila or len(fila) < c_column:
                console.print(f"[yellow]Fila incompleta en clases.csv: {fila}[/yellow]")
                continue
            id_clase, nombre, instructor, cupo = fila[:4]
            try:
                cupos = int(cupo)
            except ValueError:
                console.print(
                    f"[red]Error: cupo inválido en clase '{nombre}' ({cupo}).[/red]"
                )
                continue

            clases.append(
                {
                    "id": id_clase,
                    "nombre": nombre,
                    "instructor": instructor,
                    "cupos": cupos,
                }
            )

    try:
        with open(INSCRIPCIONES_FILE, "r", encoding="utf-8") as f:
            inscripciones = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        inscripciones = []

    inscritos_por_clase = {}
    for insc in inscripciones:
        id_clase = str(insc.get("id_clase"))
        inscritos_por_clase[id_clase] = inscritos_por_clase.get(id_clase, 0) + 1

    tabla = Table(title="CUPOS DISPONIBLES POR CLASE", style="cyan")
    tabla.add_column("ID", justify="center")
    tabla.add_column("Clase", justify="left")
    tabla.add_column("Instructor", justify="center")
    tabla.add_column("Cupos Totales", justify="center")
    tabla.add_column("Inscritos", justify="center")
    tabla.add_column("Disponibles", justify="center")

    for c in clases:
        inscritos = inscritos_por_clase.get(c["id"], 0)
        disponibles = c["cupos"] - inscritos
        color = "green" if disponibles > 0 else "red"
        tabla.add_row(
            c["id"],
            c["nombre"],
            c["instructor"],
            str(c["cupos"]),
            str(inscritos),
            f"[{color}]{disponibles}[/{color}]",
        )

    console.print(tabla)
