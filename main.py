"""
Módulo Principal - Interfaz de Usuario (UI) para Gestión de Gimnasio.

Punto de entrada de la aplicación.
Maneja la interacción con el usuario (menús, entradas, salidas) usando la librería rich.
"""

import os

import crud

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

console = Console()

# Constantes para la gestión de archivos
DIRECTORIO_DATOS = 'info'
NOMBRE_ARCHIVO_MIEMBROS = 'miembros.csv'
NOMBRE_ARCHIVO_CLASES = 'clases.csv'
NOMBRE_ARCHIVO_INSCRIPCIONES = 'inscripciones.json' # Corregido

# --- Funciones de Interfaz de Usuario con Rich (Miembros) ---

def solicitar_tipo_suscripcion(permitir_vacio: bool = False) -> str | None:
    """ Muestra un menú para que el usuario elija el tipo de suscripción. """
    console.print("\nSeleccione el tipo de suscripción:", style="cyan")

    tipos = {
        '1': 'Mensual', '2': 'Anual', '3': 'Trimestral'
    }

    opciones = list(tipos.keys())
    for key, value in tipos.items():
        console.print(f"[bold yellow]{key}[/bold yellow]. {value}")

    if permitir_vacio:
        console.print("[bold yellow]0[/bold yellow]. No cambiar")
        opciones.insert(0, '0')

    opcion = Prompt.ask("Opción", choices=opciones, show_choices=False)

    if permitir_vacio and opcion == '0':
        return None
    return tipos.get(opcion) # Usamos .get para seguridad


def menu_crear_miembro(filepath: str):
    """Maneja la lógica para registrar un nuevo miembro."""
    console.print(Panel.fit("[bold cyan]📝 Registrar Nuevo Miembro[/bold cyan]"))

    tipo_suscripcion = solicitar_tipo_suscripcion()
    nombre = Prompt.ask("Nombre completo del Miembro")

    miembro_creado = crud.crear_miembro(
        filepath, nombre, tipo_suscripcion
    )

    if miembro_creado:
        console.print(Panel(f"✅ ¡Miembro registrado con éxito!\n   ID Asignado: [bold yellow]{miembro_creado['id_miembro']}[/bold yellow]",
                            border_style="green", title="Éxito"))
    else:
        console.print(Panel("⚠️ No se pudo registrar al miembro.",
                            border_style="red", title="Error"))


def menu_leer_miembros(filepath: str):
    """Maneja la lógica para mostrar todos los miembros en una tabla."""
    console.print(Panel.fit("[bold cyan]👥 Lista de Miembros[/bold cyan]"))
    miembros = crud.leer_todos_los_miembros(filepath)

    if not miembros:
        console.print("[yellow]No hay miembros registrados.[/yellow]")
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

# Las funciones de actualización y eliminación de miembros se omiten para enfocar la corrección en la estructura.

# --- Funciones de Interfaz de Usuario con Rich (Clases) ---

def menu_crear_clase(filepath: str):
    """Maneja la lógica para registrar una nueva clase."""
    console.print(Panel.fit("[bold cyan]➕ Registrar Nueva Clase[/bold cyan]"))

    nombre_clase = Prompt.ask("Nombre de la Clase")
    instructor = Prompt.ask("Instructor")
    horario = Prompt.ask("Horario (ej. L-M-V 18:00)")
    cupo_maximo = IntPrompt.ask("Cupo Máximo", default=10)

    clase_creada = crud.crear_clase(
        filepath, nombre_clase, instructor, horario, cupo_maximo
    )

    if clase_creada:
        console.print(Panel(f"✅ ¡Clase registrada con éxito!\n   ID Asignado: [bold yellow]{clase_creada['id_clase']}[/bold yellow]",
                            border_style="green", title="Éxito"))
    else:
        console.print(Panel("⚠️ No se pudo registrar la clase.", border_style="red", title="Error"))

def menu_leer_clases(filepath: str):
    """Maneja la lógica para mostrar todas las clases en una tabla."""
    console.print(Panel.fit("[bold cyan]📋 Lista de Clases Disponibles[/bold cyan]"))
    clases = crud.leer_todas_las_clases(filepath)

    if not clases:
        console.print("[yellow]No hay clases registradas.[/yellow]")
        return

    tabla = Table(title="Clases Registradas", border_style="blue", show_header=True, header_style="bold magenta")
    tabla.add_column("ID", style="dim", width=5)
    tabla.add_column("Clase")
    tabla.add_column("Instructor")
    tabla.add_column("Horario")
    tabla.add_column("Cupo Máx.", justify="center")

    for c in clases:
        tabla.add_row(
            c.get('id_clase', 'N/D'),
            c.get('nombre_clase', 'N/D'),
            c.get('instructor', 'N/D'),
            c.get('horario', 'N/D'),
            c.get('cupo_maximo', 'N/D'),
        )

    console.print(tabla)

# --- Funciones de Interfaz de Usuario con Rich (Inscripciones) ---

def menu_inscribir_miembro(filepath_i: str, filepath_c: str):
    """Maneja la lógica para inscribir un miembro en una clase."""
    console.print(Panel.fit("[bold cyan]➡️ Inscribir Miembro en Clase[/bold cyan]"))

    # Se asume que el usuario conoce los IDs, si no, se debería listar primero.
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
    """Muestra los miembros inscritos en una clase específica."""
    console.print(Panel.fit("[bold cyan]👀 Miembros Inscritos por Clase[/bold cyan]"))
    id_clase = Prompt.ask("Ingrese el ID de la Clase")

    miembros = crud.listar_miembros_inscritos_en_clase(filepath_i, filepath_m, id_clase)

    if not miembros:
        console.print(f"No hay miembros inscritos en la clase {id_clase}.")
        return

    tabla = Table(title=f"Miembros Inscritos en Clase ID {id_clase}", border_style="blue", show_header=True, header_style="bold magenta")
    tabla.add_column("ID Miembro", style="dim", width=10)
    tabla.add_column("Nombre Completo")
    tabla.add_column("Suscripción")

    for m in miembros:
        tabla.add_row(m.get('id_miembro', 'N/D'), m.get('nombre', 'N/D'), m.get('tipo_suscripcion', 'N/D'))

    console.print(tabla)

# La función para dar de baja y listar clases por miembro se implementarían de forma similar.

# --- Menús Principales ---

def mostrar_menu_principal():
    """Imprime el menú principal en la consola."""
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
    console.print(Panel(menu_texto, title="[bold]SISTEMA DE GESTIÓN DE GIMNASIO[/bold]", subtitle="Seleccione una opción", border_style="green"))

def main():
    """Función principal que ejecuta el bucle del menú."""
    if not os.path.exists(DIRECTORIO_DATOS):
        os.makedirs(DIRECTORIO_DATOS)
        console.print(f"[green]Directorio '{DIRECTORIO_DATOS}' creado.[/green]")

    # Rutas de archivos fijas para el sistema
    path_miembros = os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_MIEMBROS)
    path_clases = os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_CLASES)
    path_inscripciones = os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_INSCRIPCIONES)

    console.print(f"\n👍 Sistema de datos inicializado en [bold green]{DIRECTORIO_DATOS}[/bold green].")

    while True:
        mostrar_menu_principal()
        opcion = Prompt.ask("Opción", choices=[str(i) for i in range(11)], show_choices=False)

        if opcion == '1':
            menu_crear_miembro(path_miembros)
        elif opcion == '2':
            menu_leer_miembros(path_miembros)
        # Opciones 3 y 4 (Actualizar/Eliminar Miembro) requerirían la implementación completa en crud.py y main.py

        elif opcion == '5':
            menu_crear_clase(path_clases)
        elif opcion == '6':
            menu_leer_clases(path_clases)

        elif opcion == '7':
            menu_inscribir_miembro(path_inscripciones, path_clases)
        elif opcion == '8':
            menu_mostrar_miembros_inscritos(path_inscripciones, path_miembros)
        # Opciones 9 y 10 (Dar de baja / Clases por miembro) requerirían la implementación de su UI.

        elif opcion == '0':
            console.print("\n[bold magenta]👋 ¡Hasta luego! Gracias por usar la gestión de gimnasio.[/bold magenta]")
            break

        # Pausa para volver al menú
        Prompt.ask("\nPresione Enter para continuar...", default="", show_default=False)

# --- Punto de Entrada del Script ---
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Programa interrumpido por el usuario. Adiós.[/bold red]")