"""
Módulo de Persistencia de Datos.

Responsable de leer y escribir datos en archivos planos (CSV y JSON).
No contiene lógica de negocio, solo operaciones de I/O.
"""

import csv
import json
import os
from typing import Any, Dict, List

# Definición de campos para las tres entidades
CAMPOS_MIEMBROS = ['id_miembro', 'nombre', 'tipo_suscripcion']
CAMPOS_CLASES = ['id_clase', 'nombre_clase', 'instructor',  'cupo_maximo']


def inicializar_archivo(filepath: str) -> None:
    """
    Verifica si un archivo de datos existe. Si no, lo crea con las cabeceras.

    Asegura que el directorio exista y, si el archivo no existe:
    - Para CSV: lo crea con las cabeceras correspondientes a Miembros o Clases.
    - Para JSON: lo crea como una lista vacía `[]`.

    :param filepath: La ruta completa al archivo de datos (ej. 'data/miembros.csv').
    :type filepath: str
    :return: None
    :rtype: None
    """
    directorio = os.path.dirname(filepath)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio)

    if not os.path.exists(filepath):
        # Determinamos los campos según el nombre del archivo
        campos = []
        if 'miembros.csv' in filepath:
            campos = CAMPOS_MIEMBROS
        elif 'clases.csv' in filepath:
            campos = CAMPOS_CLASES

        if filepath.endswith('.csv'):
            with open(filepath, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=campos)
                writer.writeheader()
        elif filepath.endswith('.json'):
            # Los archivos JSON de datos (como Inscripciones) siempre comienzan vacíos
            with open(filepath, mode='w', encoding='utf-8') as json_file:
                json.dump([], json_file)

def cargar_datos(filepath: str) -> List[Dict[str, Any]]:
    """
    Carga los datos desde un archivo (CSV o JSON) y los retorna como una lista de diccionarios.

    Asegura la inicialización del archivo antes de intentar la lectura.
    Retorna una lista vacía `[]` si el archivo no existe o está vacío/corrupto.

    :param filepath: La ruta completa al archivo de datos.
    :type filepath: str
    :return: Lista de diccionarios que representan los datos cargados.
    :rtype: List[Dict[str, Any]]
    """
    inicializar_archivo(filepath)

    try:
        if filepath.endswith('.csv'):
            with open(filepath, mode='r', newline='', encoding='utf-8') as csv_file:
                lector = csv.DictReader(csv_file)
                # Convertir a lista y asegurar que los campos numéricos se cargan como string
                return [dict(row) for row in lector]
        elif filepath.endswith('.json'):
            with open(filepath, mode='r', encoding='utf-8') as json_file:
                datos = json.load(json_file)
                return datos if isinstance(datos, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        # Captura errores comunes de lectura y retorna lista vacía
        return []

def guardar_datos(filepath: str, datos: List[Dict[str, Any]]) -> None:
    """
    Guarda una lista de diccionarios en un archivo (CSV o JSON), sobrescribiendo el contenido.

    :param filepath: La ruta completa al archivo de datos.
    :type filepath: str
    :param datos: La lista de diccionarios (datos de Miembros, Clases o Inscripciones) a guardar.
    :type datos: List[Dict[str, Any]]
    :return: None
    :rtype: None
    """
    # Determinamos los campos según el nombre del archivo (solo necesario para CSV)
    campos = []
    if 'miembros.csv' in filepath:
        campos = CAMPOS_MIEMBROS
    elif 'clases.csv' in filepath:
        campos = CAMPOS_CLASES

    if filepath.endswith('.csv'):
        with open(filepath, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=campos)
            writer.writeheader()
            writer.writerows(datos)
    elif filepath.endswith('.json'):
        with open(filepath, mode='w', encoding='utf-8') as json_file:
            json.dump(datos, json_file, indent=4)