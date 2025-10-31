# -*- coding: utf-8 -*-
"""
Módulo de Lógica de Negocio.

Contiene todas las funciones para gestionar el gimnasio (CRUD de Miembros y Clases,
y gestión de Inscripciones).
"""

from typing import Any, Dict, List, Optional
import datos

from rich.console import Console
from rich.table import Table
import csv
import os
import json

console = Console()

INFO_DIR = "info"
CLASES_FILE = os.path.join(INFO_DIR, "clases.csv")
INSCRIPCIONES_FILE = os.path.join(INFO_DIR, "inscripciones.json")

def generar_nuevo_id(entidad: str, lista: List[Dict[str, Any]]) -> str:
    """
    Genera un nuevo ID autoincremental para Miembros o Clases.

    El ID es un string que representa el número máximo actual + 1.

    :param entidad: El tipo de entidad ('miembro' o 'clase').
    :type entidad: str
    :param lista: Lista de diccionarios de la entidad (Miembros o Clases) cargada.
    :type lista: List[Dict[str, Any]]
    :return: El nuevo ID autoincremental como string.
    :rtype: str
    """
    id_key = 'id_miembro' if entidad == 'miembro' else 'id_clase'

    if not lista:
        return '1'

    # Busca el máximo ID numérico existente
    max_id = 0
    for item in lista:
        try:
            current_id = int(item.get(id_key, 0))
            if current_id > max_id:
                max_id = current_id
        except ValueError:
            # Ignora IDs no numéricos
            pass

    return str(max_id + 1)


def crear_miembro(
        filepath: str,
        nombre: str,
        tipo_suscripcion: str,
) -> Optional[Dict[str, Any]]:
    """
    (CREATE) Agrega un nuevo miembro.

    Carga los miembros existentes, genera un nuevo ID, agrega el nuevo miembro
    a la lista y guarda los datos actualizados.

    :param filepath: Ruta del archivo donde se guardan los miembros (miembros.csv).
    :type filepath: str
    :param nombre: Nombre completo del nuevo miembro.
    :type nombre: str
    :param tipo_suscripcion: Tipo de suscripción del miembro (ej. 'Mensual', 'Anual').
    :type tipo_suscripcion: str
    :return: El diccionario del miembro recién creado o None si falla la operación
             (aunque la implementación actual siempre retorna el dict).
    :rtype: Optional[Dict[str, Any]]
    """
    miembros = datos.cargar_datos(filepath)

    nuevo_id = generar_nuevo_id('miembro', miembros)

    nuevo_miembro = {
        'id_miembro': nuevo_id,
        'nombre': nombre,
        'tipo_suscripcion': tipo_suscripcion,
    }

    miembros.append(nuevo_miembro)
    datos.guardar_datos(filepath, miembros)
    return nuevo_miembro


def leer_todos_los_miembros(filepath: str) -> List[Dict[str, Any]]:
    """
    (READ) Obtiene la lista completa de miembros.

    :param filepath: Ruta del archivo donde se guardan los miembros (miembros.csv).
    :type filepath: str
    :return: Lista de diccionarios, cada uno representando un miembro.
    :rtype: List[Dict[str, Any]]
    """
    return datos.cargar_datos(filepath)


def buscar_miembro_por_id(filepath: str, id_miembro: str) -> Optional[Dict[str, Any]]:
    """
    Busca un miembro específico por su ID.

    :param filepath: Ruta del archivo donde se guardan los miembros (miembros.csv).
    :type filepath: str
    :param id_miembro: ID del miembro a buscar.
    :type id_miembro: str
    :return: El diccionario del miembro encontrado o None si no se encuentra.
    :rtype: Optional[Dict[str, Any]]
    """
    miembros = datos.cargar_datos(filepath)
    for miembro in miembros:
        if miembro.get('id_miembro') == id_miembro:
            return miembro
    return None


def actualizar_miembro(
        filepath: str,
        id_miembro: str,
        datos_nuevos: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    (UPDATE) Modifica los datos de un miembro existente.

    Busca el miembro por ID, actualiza sus campos con los `datos_nuevos`,
    y guarda la lista actualizada.

    :param filepath: Ruta del archivo donde se guardan los miembros (miembros.csv).
    :type filepath: str
    :param id_miembro: ID del miembro a actualizar.
    :type id_miembro: str
    :param datos_nuevos: Diccionario con los campos y valores a modificar.
    :type datos_nuevos: Dict[str, Any]
    :return: El diccionario del miembro actualizado o None si no se encuentra el ID.
    :rtype: Optional[Dict[str, Any]]
    """
    miembros = datos.cargar_datos(filepath)

    for i, miembro in enumerate(miembros):
        if miembro.get('id_miembro') == id_miembro:
            miembro.update(datos_nuevos)
            # Aseguramos que solo se guarden las claves definidas
            miembros[i] = {k: miembro.get(k, '') for k in datos.CAMPOS_MIEMBROS}
            datos.guardar_datos(filepath, miembros)
            return miembros[i]
    return None


def eliminar_miembro(filepath: str, id_miembro: str) -> bool:
    """
    (DELETE) Elimina un miembro.

    Carga los datos y filtra la lista para excluir el miembro con el ID dado.
    Guarda la lista si el miembro fue eliminado.

    :param filepath: Ruta del archivo donde se guardan los miembros (miembros.csv).
    :type filepath: str
    :param id_miembro: ID del miembro a eliminar.
    :type id_miembro: str
    :return: True si el miembro fue eliminado con éxito, False en caso contrario.
    :rtype: bool
    """
    miembros = datos.cargar_datos(filepath)
    miembros_iniciales = len(miembros)

    # Filtramos la lista, manteniendo solo los que NO coincidan con el ID
    miembros = [m for m in miembros if m.get('id_miembro') != id_miembro]

    if len(miembros) < miembros_iniciales:
        datos.guardar_datos(filepath, miembros)
        return True

    return False


def crear_clase(
        filepath: str,
        nombre_clase: str,
        instructor: str,
        cupo_maximo: int,
) -> Optional[Dict[str, Any]]:
    """
    (CREATE) Agrega una nueva clase.

    Carga las clases existentes, genera un nuevo ID, agrega la nueva clase
    a la lista y guarda los datos actualizados.

    :param filepath: Ruta del archivo donde se guardan las clases (clases.csv).
    :type filepath: str
    :param nombre_clase: Nombre de la clase (ej. 'Yoga', 'Spinning').
    :type nombre_clase: str
    :param instructor: Nombre del instructor a cargo de la clase.
    :type instructor: str
    :param cupo_maximo: Número máximo de participantes permitidos.
    :type cupo_maximo: int
    :return: El diccionario de la clase recién creada o None si falla la operación.
    :rtype: Optional[Dict[str, Any]]
    """
    clases = datos.cargar_datos(filepath)

    nuevo_id = generar_nuevo_id('clase', clases)

    nueva_clase = {
        'id_clase': nuevo_id,
        'nombre_clase': nombre_clase,
        'instructor': instructor,
        'cupo_maximo': str(cupo_maximo),  # Guardar como string
    }

    clases.append(nueva_clase)
    datos.guardar_datos(filepath, clases)
    return nueva_clase


def leer_todas_las_clases(filepath: str) -> List[Dict[str, Any]]:
    """
    (READ) Obtiene la lista completa de clases.

    :param filepath: Ruta del archivo donde se guardan las clases (clases.csv).
    :type filepath: str
    :return: Lista de diccionarios, cada uno representando una clase.
    :rtype: List[Dict[str, Any]]
    """
    return datos.cargar_datos(filepath)


def buscar_clase_por_id(filepath: str, id_clase: str) -> Optional[Dict[str, Any]]:
    """
    Busca una clase específica por su ID.

    :param filepath: Ruta del archivo donde se guardan las clases (clases.csv).
    :type filepath: str
    :param id_clase: ID de la clase a buscar.
    :type id_clase: str
    :return: El diccionario de la clase encontrada o None si no se encuentra.
    :rtype: Optional[Dict[str, Any]]
    """
    clases = datos.cargar_datos(filepath)
    for clase in clases:
        if clase.get('id_clase') == id_clase:
            return clase
    return None

def inscribir_miembro_en_clase(
        filepath_inscripciones: str,
        filepath_clases: str,
        id_miembro: str,
        id_clase: str
) -> tuple[bool, str]:
    """
    Inscribe a un miembro en una clase.

    Realiza validaciones de existencia de clase, duplicado de inscripción y cupo máximo.
    Si es exitoso, crea la inscripción y guarda los datos.

    :param filepath_inscripciones: Ruta del archivo de inscripciones (inscripciones.json).
    :type filepath_inscripciones: str
    :param filepath_clases: Ruta del archivo de clases (clases.csv), necesario para obtener datos de la clase.
    :type filepath_clases: str
    :param id_miembro: ID del miembro a inscribir.
    :type id_miembro: str
    :param id_clase: ID de la clase.
    :type id_clase: str
    :return: Una tupla conteniendo un booleano (True si es exitoso, False si hay error)
             y un mensaje de estado/error.
    :rtype: tuple[bool, str]
    """
    inscripciones = datos.cargar_datos(filepath_inscripciones)
    clase = buscar_clase_por_id(filepath_clases, id_clase)

    if not clase:
        return (False, f" Error: Clase con ID '{id_clase}' no encontrada.")

    # 1. Validación de duplicado
    inscritos_clase = [i for i in inscripciones if i['id_clase'] == id_clase]
    if any(i['id_miembro'] == id_miembro for i in inscritos_clase):
        return (False, f" Error: El miembro '{id_miembro}' ya está inscrito en la clase '{clase['nombre_clase']}'.")

    # 2. Validación de cupo
    cupo_maximo = int(clase.get('cupo_maximo', 0))
    if len(inscritos_clase) >= cupo_maximo:
        return (False, f" Error: La clase '{clase['nombre_clase']}' ha alcanzado su cupo máximo ({cupo_maximo}).")

    nueva_inscripcion = {'id_miembro': id_miembro, 'id_clase': id_clase}
    inscripciones.append(nueva_inscripcion)
    datos.guardar_datos(filepath_inscripciones, inscripciones)
    return (True, f"¡Inscripción exitosa! Miembro {id_miembro} en clase {clase['nombre_clase']}.")


def dar_baja_miembro_de_clase(filepath: str, id_miembro: str, id_clase: str) -> bool:
    """
    Da de baja a un miembro de una clase (elimina la inscripción).

    Carga las inscripciones y filtra la lista para excluir la inscripción
    que coincida con el par (ID de miembro, ID de clase).

    :param filepath: Ruta del archivo de inscripciones (inscripciones.json).
    :type filepath: str
    :param id_miembro: ID del miembro a dar de baja.
    :type id_miembro: str
    :param id_clase: ID de la clase de la que se dará de baja.
    :type id_clase: str
    :return: True si la inscripción fue eliminada con éxito, False en caso contrario.
    :rtype: bool
    """

    inscripciones = datos.cargar_datos(filepath)
    inscripciones_iniciales = len(inscripciones)

    inscripciones = [
        i for i in inscripciones
        if not (i.get('id_miembro') == id_miembro and i.get('id_clase') == id_clase)
    ]

    if len(inscripciones) < inscripciones_iniciales:
        datos.guardar_datos(filepath, inscripciones)
        return True

    return False


def listar_miembros_inscritos_en_clase(filepath_inscripciones: str, filepath_miembros: str, id_clase: str) -> List[
    Dict[str, Any]]:
    """
    Muestra la lista de miembros inscritos en una clase específica.

    Obtiene los IDs de los miembros inscritos en la clase dada, y luego
    busca los detalles completos de esos miembros.

    :param filepath_inscripciones: Ruta del archivo de inscripciones (inscripciones.json).
    :type filepath_inscripciones: str
    :param filepath_miembros: Ruta del archivo de miembros (miembros.csv).
    :type filepath_miembros: str
    :param id_clase: ID de la clase cuyos miembros inscritos se desean listar.
    :type id_clase: str
    :return: Lista de diccionarios, cada uno con los detalles de un miembro inscrito.
    :rtype: List[Dict[str, Any]]
    """
    inscripciones = datos.cargar_datos(filepath_inscripciones)
    miembros_todos = datos.cargar_datos(filepath_miembros)

    ids_inscritos = [i['id_miembro'] for i in inscripciones if i['id_clase'] == id_clase]

    miembros_inscritos = [
        m for m in miembros_todos
        if m.get('id_miembro') in ids_inscritos
    ]
    return miembros_inscritos


def listar_clases_inscritas_por_miembro(filepath_inscripciones: str, filepath_clases: str, id_miembro: str) -> List[
    Dict[str, Any]]:
    """
    Muestra todas las clases en las que está inscrito un miembro.

    Obtiene los IDs de las clases en las que está inscrito el miembro dado,
    y luego busca los detalles completos de esas clases.

    :param filepath_inscripciones: Ruta del archivo de inscripciones (inscripciones.json).
    :type filepath_inscripciones: str
    :param filepath_clases: Ruta del archivo de clases (clases.csv).
    :type filepath_clases: str
    :param id_miembro: ID del miembro cuyas clases inscritas se desean listar.
    :type id_miembro: str
    :return: Lista de diccionarios, cada uno con los detalles de una clase inscrita.
    :rtype: List[Dict[str, Any]]
    """
    inscripciones = datos.cargar_datos(filepath_inscripciones)
    clases_todas = datos.cargar_datos(filepath_clases)

    ids_clases = [i['id_clase'] for i in inscripciones if i['id_miembro'] == id_miembro]

    clases_inscritas = [
        c for c in clases_todas
        if c.get('id_clase') in ids_clases
    ]
    return clases_inscritas
def ver_cupos_disponibles():
    """
    Muestra los cupos disponibles por clase leyendo clases.csv e inscripciones.json.
    Si el CSV no tiene columna de cupos, se asigna un valor por defecto (10).
    """
    if not os.path.exists(CLASES_FILE):
        console.print("[red]El archivo de clases no existe.[/red]")
        return

    if not os.path.exists(INSCRIPCIONES_FILE):
        console.print("[red]El archivo de inscripciones no existe.[/red]")
        return

    clases = []
    with open(CLASES_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # <- 🔹 omite la primera fila
        for fila in reader:
            if not fila:
                continue
            if len(fila) < 4:
                console.print(f"[yellow]La clase con ID {fila[0]} no tiene cupos definidos. Se omitirá.[/yellow]")
                continue

            try:
                cupos = int(fila[3])
            except ValueError:
                console.print(f"[red]Error: cupos inválidos en la clase {fila[1]} ({fila[3]}).[/red]")
                continue

            clases.append({
                "id": fila[0],
                "nombre": fila[1],
                "tipo": fila[2],
                "cupos": cupos
            })

    try:
        with open(INSCRIPCIONES_FILE, "r", encoding="utf-8") as f:
            inscripciones = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        inscripciones = []

    inscritos_por_clase = {}
    for insc in inscripciones:
        id_clase = str(insc.get("id_clase"))
        inscritos_por_clase[id_clase] = inscritos_por_clase.get(id_clase, 0) + 1

    # Crear tabla con Rich
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
            c["id"], c["nombre"], c["tipo"],
            str(c["cupos"]), str(inscritos),
            f"[{color}]{disponibles}[/{color}]"
        )

    console.print(tabla)