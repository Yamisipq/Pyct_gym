"""
Módulo Principal - Interfaz de Usuario (UI) para Gestión de Gimnasio.

Punto de entrada de la aplicación.
Maneja la interacción con el usuario (menús, entradas, salidas) usando la librería rich.
"""

import os
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

import crud

console = Console()

# Constantes para la gestión de archivos
DIRECTORIO_DATOS = 'info'
NOMBRE_ARCHIVO_MIEMBROS = 'miembros.csv'
NOMBRE_ARCHIVO_CLASES = 'clases.csv'
NOMBRE_ARCHIVO_INSCRIPCIONES = 'inscripciones.json'

# --- Funciones de Interfaz de Usuario con Rich (Miembros) ---

def solicitar_tipo_suscripcion(permitir_vacio: bool = False) -> Optional[str]:
    """
    Muestra un menú para que el usuario elija el tipo de suscripción.

    :param permitir_vacio: Si es True, incluye la opción '0. No cambiar'.
    :type permitir_vacio: bool
    :return: El tipo de suscripción seleccionado (ej. 'Mensual'),
    None si se elige 'No cambiar'o None en caso de error.
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
    return tipos.get(opcion)


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
        console.print(Panel(f"¡Miembro registrado con éxito!\n   "
                            f"ID Asignado: {miembro_creado['id_miembro']}",
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

    tabla = Table(title="Miembros Registrados", border_style="blue", show_header=True,
                  header_style="bold magenta")
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

# --- Funciones de Interfaz de Usuario (Clases) ---

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
    cupo_maximo = IntPrompt.ask("Cupo Máximo", default=10)

    clase_creada = crud.crear_clase(filepath, nombre_clase, instructor, cupo_maximo)

    if clase_creada:
        console.print(Panel(
            f"¡Clase registrada con éxito!\nID Asignado: {clase_creada['id_clase']}",
            border_style="green", title="Éxito"
        ))
    else:
        console.print(Panel("No se pudo registrar la clase.",
                            border_style="red", title="Error"))


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

    tabla = Table(title="Clases Registradas", border_style="blue", show_header=True,
                  header_style="bold magenta")
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

# --- Funciones de Interfaz de Usuario con Rich (Inscripciones) ---

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
    :param filepath_m: Ruta del archivo de miembros.
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

    tabla = Table(title=f"Miembros Inscritos en Clase ID {id_clase}",
                  border_style="blue",
                  show_header=True,
                  header_style="bold magenta")
    tabla.add_column("ID Miembro", style="dim", width=10)
    tabla.add_column("Nombre Completo")
    tabla.add_column("Suscripción")

    for m in miembros:
        tabla.add_row(m.get('id_miembro', 'N/D'), m.get('nombre', 'N/D'),
                      m.get('tipo_suscripcion', 'N/D'))

    console.print(tabla)

# --- Menús Principales ---

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
        "10.Mostrar clases de un miembro\n\n"
        "0.Salir"
    )
    console.print(Panel(menu_texto, title="SISTEMA DE GESTIÓN DE GIMNASIO",
    subtitle="Seleccione una opción", border_style="green"))


def clases_miembro(path_clases: str, path_inscripciones: str):
    """Muestra las clases en las que está inscrito un miembro."""
    console.print(Panel.fit("Clases de un Miembro"))
    id_miembro = Prompt.ask("Ingrese el ID del miembro")

    clases = (crud.listar_clases_inscritas_por_miembro
              (path_inscripciones, path_clases, id_miembro))

    if not clases:
        console.print(f"El miembro ID {id_miembro} "
                      "no está inscrito en ninguna clase.")
    else:
        tabla = Table(title=f"Clases de Miembro ID {id_miembro}",
                      border_style="blue", show_header=True,
                      header_style="bold magenta")
        tabla.add_column("ID Clase", style="dim", width=10)
        tabla.add_column("Clase")
        tabla.add_column("Instructor")

        for c in clases:
            tabla.add_row(
                c.get('id_clase', 'N/D'),
                c.get('nombre_clase', 'N/D'),
                c.get('instructor', 'N/D')
            )

        console.print(tabla)


def baja_miembro(path_inscripciones: str):
    """Da de baja a un miembro de una clase específica."""
    id_miembro = Prompt.ask("Ingrese el ID del miembro")
    id_clase = Prompt.ask("Ingrese el ID de la clase")

    exito = (crud.dar_baja_miembro_de_clase
             (path_inscripciones, id_miembro, id_clase))

    if exito:
        console.print(Panel("Miembro dado de baja.",
                            border_style="green", title="Éxito"))
    else:
        console.print(Panel("No se encontró inscripción con esos datos.",
                            border_style="red", title="Error"))


def elim_miembro(path_miembros: str, path_inscripciones: str):
    """Elimina un miembro del sistema y todas sus inscripciones."""
    id_miembro = Prompt.ask("Ingrese el ID del miembro a eliminar:",
                            show_choices=False)

    confirmar = Prompt.ask(
        f"¿Está seguro de eliminar el miembro {id_miembro}? "
        "(Se eliminarán también todas sus inscripciones)",
        choices=["si", "no"], default="no")

    if confirmar.lower() == "si":
        if crud.eliminar_miembro(path_miembros, id_miembro, path_inscripciones):
            console.print("\n[green] ✓ [/green] Miembro y sus inscripciones eliminados exitosamente")
        else:
            console.print(f"\n[red]✗[/red] "
                          f"No se encontró el miembro con ID: {id_miembro}")
    else:
        console.print("\n[yellow]Operación cancelada[/yellow]")


def actz_miembros(path_miembros: str):
    """Actualiza los datos de un miembro existente."""
    id_miembro = Prompt.ask("Ingrese el ID de miembro:", show_choices=False)

    console.print("\n[bold cyan]Actualizar Miembro[/bold cyan]")
    console.print("Deje en blanco los campos que no desea modificar\n")

    datos_nuevos = {}

    nombre = Prompt.ask("Ingrese nombre:", show_choices=False)
    if nombre:
        datos_nuevos['nombre'] = nombre

    tipo_suscripcion = solicitar_tipo_suscripcion(permitir_vacio=True)
    if tipo_suscripcion:
        datos_nuevos['tipo_suscripcion'] = tipo_suscripcion

    miembro_actualizado = (
        crud.actualizar_miembro
        (path_miembros, id_miembro, datos_nuevos))

    if miembro_actualizado:
        console.print("\n[green] ✓ [/green] "
                      "Miembro actualizado exitosamente")
    else:
        console.print(f"\n[red] ✗ [/red] "
                      f"No se encontró el miembro con ID: {id_miembro}")


def inicializar_directorios():
    """Crea el directorio de datos si no existe."""
    if not os.path.exists(DIRECTORIO_DATOS):
        os.makedirs(DIRECTORIO_DATOS)
        console.print(f"Directorio '{DIRECTORIO_DATOS}' creado.")


def obtener_rutas_archivos():
    """
    Retorna las rutas de los archivos del sistema.

    :return: Tupla con (path_miembros, path_clases, path_inscripciones)
    :rtype: tuple
    """
    path_miembros = os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_MIEMBROS)
    path_clases = os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_CLASES)
    path_inscripciones = os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_INSCRIPCIONES)
    return path_miembros, path_clases, path_inscripciones


def procesar_opcion(opcion: str, path_miembros: str, path_clases: str,
                    path_inscripciones: str) -> bool:
    """
    Procesa la opción seleccionada por el usuario.

    :param opcion: Opción del menú seleccionada.
    :type opcion: str
    :param path_miembros: Ruta del archivo de miembros.
    :type path_miembros: str
    :param path_clases: Ruta del archivo de clases.
    :type path_clases: str
    :param path_inscripciones: Ruta del archivo de inscripciones.
    :type path_inscripciones: str
    :return: False si el usuario elige salir, True en otro caso.
    :rtype: bool
    """
    if opcion == '1':
        menu_crear_miembro(path_miembros)
    elif opcion == '2':
        menu_leer_miembros(path_miembros)
    elif opcion == '3':
        actz_miembros(path_miembros)
    elif opcion == '4':
        elim_miembro(path_miembros, path_inscripciones)
    elif opcion == '5':
        menu_crear_clase(path_clases)
    elif opcion == '6':
        menu_leer_clases(path_clases)
    elif opcion == '7':
        menu_inscribir_miembro(path_inscripciones, path_clases)
    elif opcion == '8':
        menu_mostrar_miembros_inscritos(path_inscripciones, path_miembros)
    elif opcion == '9':
        baja_miembro(path_inscripciones)
    elif opcion == '10':
        clases_miembro(path_clases, path_inscripciones)
    elif opcion == '0':
        console.print("\n¡Hasta luego! Gracias por usar la gestión de gimnasio.")
        return False
    return True


def main():
    """
    Función principal que ejecuta el bucle del menú.

    Inicializa el directorio de datos, define las rutas de los archivos
    y maneja la navegación del menú principal, llamando a las funciones
    de UI correspondientes a cada opción.

    :return: None
    :rtype: None
    """
    inicializar_directorios()
    path_miembros, path_clases, path_inscripciones = obtener_rutas_archivos()

    console.print(f"\nSistema de datos inicializado en {DIRECTORIO_DATOS}.")

    while True:
        mostrar_menu_principal()
        opcion = Prompt.ask("Opción", choices=[str(i) for i in range(11)],
                            show_choices=False)

        continuar = procesar_opcion(opcion, path_miembros, path_clases,
                                    path_inscripciones)

        if not continuar:
            break

        Prompt.ask("\nPresione Enter para continuar...", default="", show_default=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\nAdiós.")