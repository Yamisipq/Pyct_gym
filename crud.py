# -*- coding: utf-8 -*-
"""
Módulo de Lógica de Negocio.

Contiene todas las funciones para gestionar el gimnasio (CRUD de Miembros y Clases,
y gestión de Inscripciones).
"""

from typing import Any, Dict, List, Optional
import datos


# --- Funciones Auxiliares ---

def generar_nuevo_id(entidad: str, lista: List[Dict[str, Any]]) -> str:
    """
    Genera un nuevo ID autoincremental para Miembros o Clases.
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


# --- CRUD de Miembros (Persistencia en miembros.csv) ---

def crear_miembro(
        filepath: str,
        nombre: str,
        tipo_suscripcion: str,
) -> Optional[Dict[str, Any]]:
    """
    (CREATE) Agrega un nuevo miembro.
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
    """ (READ) Obtiene la lista completa de miembros. """
    return datos.cargar_datos(filepath)


def buscar_miembro_por_id(filepath: str, id_miembro: str) -> Optional[Dict[str, Any]]:
    """ Busca un miembro específico por su ID. """
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
    """
    miembros = datos.cargar_datos(filepath)
    miembros_iniciales = len(miembros)

    # Filtramos la lista, manteniendo solo los que NO coincidan con el ID
    miembros = [m for m in miembros if m.get('id_miembro') != id_miembro]

    if len(miembros) < miembros_iniciales:
        datos.guardar_datos(filepath, miembros)
        return True

    return False


# --- CRUD de Clases (Persistencia en clases.csv) ---

def crear_clase(
        filepath: str,
        nombre_clase: str,
        instructor: str,
        horario: str,
        cupo_maximo: int,
) -> Optional[Dict[str, Any]]:
    """
    (CREATE) Agrega una nueva clase.
    """
    clases = datos.cargar_datos(filepath)

    nuevo_id = generar_nuevo_id('clase', clases)

    nueva_clase = {
        'id_clase': nuevo_id,
        'nombre_clase': nombre_clase,
        'instructor': instructor,
        'horario': horario,
        'cupo_maximo': str(cupo_maximo),  # Guardar como string
    }

    clases.append(nueva_clase)
    datos.guardar_datos(filepath, clases)
    return nueva_clase


def leer_todas_las_clases(filepath: str) -> List[Dict[str, Any]]:
    """ (READ) Obtiene la lista completa de clases. """
    return datos.cargar_datos(filepath)


def buscar_clase_por_id(filepath: str, id_clase: str) -> Optional[Dict[str, Any]]:
    """ Busca una clase específica por su ID. """
    clases = datos.cargar_datos(filepath)
    for clase in clases:
        if clase.get('id_clase') == id_clase:
            return clase
    return None


# Las funciones de actualización y eliminación de clases son similares a las de Miembros,
# se omiten por espacio, pero se implementarían de forma análoga.

# --- Gestión de Inscripciones (Persistencia en inscripciones.json) ---

def inscribir_miembro_en_clase(
        filepath_inscripciones: str,
        filepath_clases: str,
        id_miembro: str,
        id_clase: str
) -> tuple[bool, str]:
    """
    Inscribe a un miembro en una clase.

    Retorna (True, mensaje_exito) o (False, mensaje_error).
    """
    inscripciones = datos.cargar_datos(filepath_inscripciones)
    clase = buscar_clase_por_id(filepath_clases, id_clase)

    if not clase:
        return (False, f"❌ Error: Clase con ID '{id_clase}' no encontrada.")

    # 1. Validación de duplicado
    inscritos_clase = [i for i in inscripciones if i['id_clase'] == id_clase]
    if any(i['id_miembro'] == id_miembro for i in inscritos_clase):
        return (False, f"❌ Error: El miembro '{id_miembro}' ya está inscrito en la clase '{clase['nombre_clase']}'.")

    # 2. Validación de cupo
    cupo_maximo = int(clase.get('cupo_maximo', 0))
    if len(inscritos_clase) >= cupo_maximo:
        return (False, f"❌ Error: La clase '{clase['nombre_clase']}' ha alcanzado su cupo máximo ({cupo_maximo}).")

    # 3. Creación de inscripción
    nueva_inscripcion = {'id_miembro': id_miembro, 'id_clase': id_clase}
    inscripciones.append(nueva_inscripcion)
    datos.guardar_datos(filepath_inscripciones, inscripciones)
    return (True, f"✅ ¡Inscripción exitosa! Miembro {id_miembro} en clase {clase['nombre_clase']}.")


def dar_baja_miembro_de_clase(filepath: str, id_miembro: str, id_clase: str) -> bool:
    """
    Da de baja a un miembro de una clase.
    """
    inscripciones = datos.cargar_datos(filepath)
    inscripciones_iniciales = len(inscripciones)

    # Filtramos para mantener solo las inscripciones que NO coincidan con el par (miembro, clase)
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
    """
    inscripciones = datos.cargar_datos(filepath_inscripciones)
    clases_todas = datos.cargar_datos(filepath_clases)

    ids_clases = [i['id_clase'] for i in inscripciones if i['id_miembro'] == id_miembro]

    clases_inscritas = [
        c for c in clases_todas
        if c.get('id_clase') in ids_clases
    ]
    return clases_inscritas