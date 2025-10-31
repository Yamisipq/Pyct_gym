"""
Módulo Principal - Interfaz de Usuario (UI) para Gestión de Gimnasio.

Punto de entrada de la aplicación.
Maneja la interacción con el usuario (menús, entradas, salidas) usando la librería rich.
"""

import os

import crud

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from typing import Optional, List

from crud import actualizar_miembro, eliminar_miembro, dar_baja_miembro_de_clase, \
    listar_clases_inscritas_por_miembro

console = Console()

# Constantes para la gestión de archivos
DIRECTORIO_DATOS = 'info'
NOMBRE_ARCHIVO_MIEMBROS = 'miembros.csv'
NOMBRE_ARCHIVO_CLASES = 'clases.csv'
NOMBRE_ARCHIVO_INSCRIPCIONES = 'inscripciones.json' # Corregido

# --- Funciones de Interfaz de Usuario con Rich (Miembros) ---

def solicitar_tipo_suscripcion(permitir_vacio: bool = False) -> Optional[str]:
    """
    Muestra un menú para que el usuario elija el tipo de suscripción.

    :param permitir_vacio: Si es True, incluye la opción '0. No cambiar' (útil para actualizaciones).
    :type permitir_vacio: bool
    :return: El tipo de suscripción seleccionado (ej. 'Mensual'), None si se elige 'No cambiar', o None en caso de error.
    :rtype: Optional[str]
    """
    console.print("\nSeleccione el tipo de suscripción:", style="cyan")

    tipos = {
        '1': 'Mensual', '2': 'Anual'
    }

    opciones = list(tipos.keys())
    for key, value in tipos.items():
        console.print(f"{key}. {value}")

    if permitir_vacio:
        console.print("0. No cambiar")
        opciones.insert(0, '0')

    opcion = Prompt.ask("Opción", choices=opciones, show_choices=False)

    if permitir_vacio and opcion == '0':
        return None
    return tipos.get(opcion) # Usamos .get para seguridad


def menu_crear_miembro(filepath: str):
    """
    Maneja la lógica para registrar un nuevo miembro.

    Solicita al usuario el nombre y el tipo de suscripción, llama a la función
    CRUD de creación y muestra el resultado (incluyendo el ID asignado).

    :param filepath: Ruta del archivo de miembros.
    :type filepath: str
    :return: None
    :rtype: None
    """
    console.print(Panel.fit("Registrar Nuevo Miembro"))

    tipo_suscripcion = solicitar_tipo_suscripcion()
    nombre = Prompt.ask("Nombre completo del Miembro")

    miembro_creado = crud.crear_miembro(
        filepath, nombre, tipo_suscripcion
    )

    if miembro_creado:
        console.print(Panel(f"¡Miembro registrado con éxito!\n   ID Asignado: {miembro_creado['id_miembro']}",
                            border_style="green", title="Éxito"))
    else:
        console.print(Panel("No se pudo registrar al miembro.",
                            border_style="red", title="Error"))

def menu_leer_miembros(filepath: str):
    """
    Maneja la lógica para mostrar todos los miembros en una tabla.

    Carga todos los miembros y los presenta en una tabla formateada con rich.

    :param filepath: Ruta del archivo de miembros.
    :type filepath: str
    :return: None
    :rtype: None
    """
    console.print(Panel.fit("Lista de Miembros"))
    miembros = crud.leer_todos_los_miembros(filepath)

    if not miembros:
        console.print("No hay miembros registrados.")
        return

    tabla = Table(title="Miembros Registrados", border_style="blue", show_header=True, header_style="bold magenta")
    tabla.add_column("ID", style="dim", width=5)
    tabla.add_column("Nombre Completo")
    tabla.add_column("Suscripción", justify="center")

    miembros_ordenados = sorted(miembros, key=lambda x: str(x.get('id_miembro', '0')))

    for m in miembros_ordenados:
        tabla.add_row(
            m.get('id_miembro', 'N/D'),
            m.get('nombre', 'N/D'),
            m.get('tipo_suscripcion', 'N/D'),
        )

    console.print(tabla)


def menu_crear_clase(filepath: str):
    """
    Maneja la lógica para registrar una nueva clase.

    Solicita al usuario los datos de la clase (nombre, instructor, cupo),
    llama a la función CRUD de creación y muestra el resultado.

    :param filepath: Ruta del archivo de clases.
    :type filepath: str
    :return: None
    :rtype: None
    """
    console.print(Panel.fit("Registrar Nueva Clase"))
    nombre_clase = Prompt.ask("Nombre de la Clase")
    instructor = Prompt.ask("Instructor")
    cupo_maximo = IntPrompt.ask("Cupo Máximo")

    clase_creada = crud.crear_clase(filepath, nombre_clase, instructor, cupo_maximo)

    if clase_creada:
        console.print(Panel(
            f"¡Clase registrada con éxito!\nID Asignado: {clase_creada['id_clase']}",
            border_style="green", title="Éxito"
        ))
    else:
        console.print(Panel("No se pudo registrar la clase.", border_style="red", title="Error"))


def menu_leer_clases(filepath: str):
    """
    Maneja la lógica para mostrar todas las clases en una tabla.

    Carga todas las clases y las presenta en una tabla formateada con rich.

    :param filepath: Ruta del archivo de clases.
    :type filepath: str
    :return: None
    :rtype: None
    """
    console.print(Panel.fit("Lista de Clases Disponibles"))
    clases = crud.leer_todas_las_clases(filepath)

    if not clases:
        console.print("No hay clases registradas.")
        return

    tabla = Table(title="Clases Registradas", border_style="blue", show_header=True, header_style="bold magenta")
    tabla.add_column("ID", style="dim", width=5)
    tabla.add_column("Clase")
    tabla.add_column("Instructor")
    tabla.add_column("Cupo Máx.", justify="center")

    for c in clases:
        tabla.add_row(
            c.get('id_clase', 'N/D'),
            c.get('nombre_clase', 'N/D'),
            c.get('instructor', 'N/D'),
            c.get('cupo_maximo', 'N/D'),
        )

    console.print(tabla)


def menu_inscribir_miembro(filepath_i: str, filepath_c: str):
    """
    Maneja la lógica para inscribir un miembro en una clase.

    Solicita los IDs de miembro y clase, llama a la función CRUD de inscripción
    y muestra el resultado de la operación (éxito o error de validación/cupo).

    :param filepath_i: Ruta del archivo de inscripciones.
    :type filepath_i: str
    :param filepath_c: Ruta del archivo de clases (necesario para validaciones de cupo).
    :type filepath_c: str
    :return: None
    :rtype: None
    """
    console.print(Panel.fit("Inscribir Miembro en Clase"))

    id_miembro = Prompt.ask("Ingrese el ID del Miembro")
    id_clase = Prompt.ask("Ingrese el ID de la Clase")

    exito, mensaje = crud.inscribir_miembro_en_clase(
        filepath_i, filepath_c, id_miembro, id_clase
    )

    if exito:
        console.print(Panel(mensaje, border_style="green", title="Éxito"))
    else:
        console.print(Panel(mensaje, border_style="red", title="Error"))

def menu_mostrar_miembros_inscritos(filepath_i: str, filepath_m: str):
    """
    Muestra los miembros inscritos en una clase específica.

    Solicita el ID de la clase, recupera la lista de miembros inscritos
    y la presenta en una tabla.

    :param filepath_i: Ruta del archivo de inscripciones.
    :type filepath_i: str
    :param filepath_m: Ruta del archivo de miembros (necesario para obtener los detalles de los miembros).
    :type filepath_m: str
    :return: None
    :rtype: None
    """
    console.print(Panel.fit("Miembros Inscritos por Clase"))
    id_clase = Prompt.ask("Ingrese el ID de la Clase")

    miembros = crud.listar_miembros_inscritos_en_clase(filepath_i, filepath_m, id_clase)

    if not miembros:
        console.print(f"No hay miembros inscritos en la clase ID '{id_clase}'.")
        return

    tabla = Table(title=f"Miembros Inscritos en Clase ID {id_clase}", border_style="blue", show_header=True, header_style="bold magenta")
    tabla.add_column("ID Miembro", style="dim", width=10)
    tabla.add_column("Nombre Completo")
    tabla.add_column("Suscripción")

    for m in miembros:
        tabla.add_row(m.get('id_miembro', 'N/D'), m.get('nombre', 'N/D'), m.get('tipo_suscripcion', 'N/D'))

    console.print(tabla)

def mostrar_menu_principal():
    """
    Imprime el menú principal de la aplicación en la consola.

    Utiliza un Panel de rich para mejorar la presentación del menú de opciones.

    :return: None
    :rtype: None
    """
    menu_texto = (
        "-- GESTIÓN DE MIEMBROS --\n"
        "1.Registrar nuevo miembro\n"
        "2.Ver todos los miembros\n"
        "3.Actualizar datos de miembro\n"
        "4.Eliminar miembro\n\n"
        "-- GESTIÓN DE CLASES --\n"
        "5.Registrar nueva clase\n"
        "6.Ver todas las clases\n\n"
        "-- GESTIÓN DE INSCRIPCIONES --\n"
        "7.Inscribir miembro en clase\n"
        "8.Listar miembros inscritos en clase\n"
        "9.Dar de baja a un miembro de clase\n"
        "10.Mostrar clases de un miembro\n"
        "11. Ver cupos disponibles por clase\n\n"
        "0.Salir"
    )
    console.print(Panel(menu_texto, title="SISTEMA DE GESTIÓN DE GIMNASIO", subtitle="Seleccione una opción", border_style="green"))


def submenu_miembros(path_miembros):
    while True:
        console.print(Panel(
            "1. Registrar nuevo miembro\n"
            "2. Ver todos los miembros\n"
            "3. Actualizar miembro\n"
            "4. Eliminar miembro\n"
            "0. Volver al menú principal",
            title="Submenú - Gestión de Miembros",
            border_style="cyan"
        ))

        opcion = Prompt.ask("Opción", choices=["0", "1", "2", "3", "4"], show_choices=False)

        if opcion == "1":
            menu_crear_miembro(path_miembros)
        elif opcion == "2":
            menu_leer_miembros(path_miembros)
        elif opcion == "3":
            id_miembro = Prompt.ask("Ingrese el ID de miembro:")
            console.print("\n[bold cyan]Actualizar Miembro[/bold cyan]")
            datos_nuevos = {}
            nombre = Prompt.ask("Nuevo nombre (opcional)", default="")
            tipo = Prompt.ask("Nuevo tipo de membresía (Mensual/Anual, opcional)", default="")
            if nombre:
                datos_nuevos["nombre"] = nombre
            if tipo:
                datos_nuevos["tipo_suscripcion"] = tipo
            if actualizar_miembro(path_miembros, id_miembro, datos_nuevos):
                console.print("[green]✓ Miembro actualizado exitosamente[/green]")
            else:
                console.print("[red]✗ No se encontró el miembro[/red]")
        elif opcion == "4":
            id_miembro = Prompt.ask("Ingrese el ID del miembro a eliminar")
            confirmar = Prompt.ask(f"¿Eliminar miembro {id_miembro}?", choices=["si", "no"], default="no")
            if confirmar == "si":
                if eliminar_miembro(path_miembros, id_miembro):
                    console.print("[green]Miembro eliminado.[/green]")
                else:
                    console.print("[red]No se encontró el miembro.[/red]")
        elif opcion == "0":
            break

        Prompt.ask("\nPresione Enter para continuar...", default="", show_default=False)


def submenu_clases(path_clases):
    while True:
        console.print(Panel(
            "1. Registrar nueva clase\n"
            "2. Ver todas las clases\n"
            "0. Volver al menú principal",
            title="Submenú - Gestión de Clases",
            border_style="cyan"
        ))

        opcion = Prompt.ask("Opción", choices=["0", "1", "2"], show_choices=False)

        if opcion == "1":
            menu_crear_clase(path_clases)
        elif opcion == "2":
            menu_leer_clases(path_clases)
        elif opcion == "0":
            break

        Prompt.ask("\nPresione Enter para continuar...", default="", show_default=False)


def submenu_inscripciones(path_inscripciones, path_clases, path_miembros):
    while True:
        console.print(Panel(
            "1. Inscribir miembro en clase\n"
            "2. Listar miembros inscritos en una clase\n"
            "3. Dar de baja miembro de clase\n"
            "4. Ver clases de un miembro\n"
            "5. Ver cupos disponibles\n"
            "0. Volver al menú principal",
            title="Submenú - Inscripciones",
            border_style="cyan"
        ))

        opcion = Prompt.ask("Opción", choices=[str(i) for i in range(6)], show_choices=False)

        if opcion == "1":
            menu_inscribir_miembro(path_inscripciones, path_clases)
        elif opcion == "2":
            menu_mostrar_miembros_inscritos(path_inscripciones, path_miembros)
        elif opcion == "3":
            id_miembro = Prompt.ask("Ingrese el ID del miembro")
            id_clase = Prompt.ask("Ingrese el ID de la clase")
            if dar_baja_miembro_de_clase(path_inscripciones, id_miembro, id_clase):
                console.print("[green]Miembro dado de baja exitosamente[/green]")
            else:
                console.print("[red]No se encontró inscripción[/red]")
        elif opcion == "4":
            id_miembro = Prompt.ask("Ingrese el ID del miembro")
            clases = listar_clases_inscritas_por_miembro(path_inscripciones, path_clases, id_miembro)
            if not clases:
                console.print(f"El miembro ID {id_miembro} no está inscrito en ninguna clase.")
            else:
                tabla = Table(title=f"Clases de Miembro ID {id_miembro}")
                tabla.add_column("ID Clase")
                tabla.add_column("Clase")
                tabla.add_column("Instructor")
                for c in clases:
                    tabla.add_row(c.get("id_clase", ""), c.get("nombre_clase", ""), c.get("instructor", ""))
                console.print(tabla)
        elif opcion == "5":
            from crud import ver_cupos_disponibles
            ver_cupos_disponibles()
        elif opcion == "0":
            break

        Prompt.ask("\nPresione Enter para continuar...", default="", show_default=False)


def main():
    if not os.path.exists(DIRECTORIO_DATOS):
        os.makedirs(DIRECTORIO_DATOS)

    path_miembros = os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_MIEMBROS)
    path_clases = os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_CLASES)
    path_inscripciones = os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_INSCRIPCIONES)

    while True:
        console.print(Panel(
            "1. Gestión de Miembros\n"
            "2. Gestión de Clases\n"
            "3. Gestión de Inscripciones\n"
            "0. Salir",
            title="Menú Principal",
            border_style="green"
        ))

        opcion = Prompt.ask("Opción", choices=["0", "1", "2", "3"], show_choices=False)

        if opcion == "1":
            submenu_miembros(path_miembros)
        elif opcion == "2":
            submenu_clases(path_clases)
        elif opcion == "3":
            submenu_inscripciones(path_inscripciones, path_clases, path_miembros)
        elif opcion == "0":
            console.print("\n¡Hasta luego!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\nPrograma interrumpido por el usuario. Adiós.")