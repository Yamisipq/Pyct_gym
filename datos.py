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
CAMPOS_CLASES = ['id_clase', 'nombre_clase', 'instructor', 'horario', 'cupo_maximo']


def inicializar_archivo(filepath: str) -> None:
    """
    Verifica si un archivo de datos existe. Si no, lo crea con las cabeceras.

    Args:
        filepath (str): La ruta completa al archivo de datos.
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
        return []

def guardar_datos(filepath: str, datos: List[Dict[str, Any]]) -> None:
    """
    Guarda una lista de diccionarios en un archivo (CSV o JSON), sobrescribiendo el contenido.
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