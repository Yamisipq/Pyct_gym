# -*- coding: utf-8 -*-
"""
Sistema de gestión de gimnasio
--------------------------------
Permite administrar miembros, clases e inscripciones.
"""

import os
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel

import crud
import datos

console = Console()

INFO_DIR = "info"
MIEMBROS_FILE = os.path.join(INFO_DIR, "miembros.csv")
CLASES_FILE = os.path.join(INFO_DIR, "clases.csv")
INSCRIPCIONES_FILE = os.path.join(INFO_DIR, "inscripciones.json")


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def solicitar_tipo_suscripcion(permitir_vacio: bool = False) -> Optional[str]:
    """
    Muestra un menú para que el usuario elija el tipo de suscripción.

    :param permitir_vacio: Si es True, incluye la opción '0. No cambiar'.
    :return: Tipo de suscripción o None si el usuario elige no cambiar.
    """
    console.print("\nSeleccione el tipo de suscripción:", style="cyan")

    tipos = {
        '1': 'Mensual',
        '2': 'Anual'
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


def pausar():
    input("\nPresione [Enter] para continuar...")


def mostrar_tabla(lista, titulo):
    """Muestra una lista de diccionarios en formato de tabla con estilo mejorado."""
    if not lista:
        console.print("[yellow]No hay datos para mostrar.[/yellow]")
        return

    tabla = Table(title=f"[bold green]{titulo}[/bold green]", style="cyan", show_lines=True)

    # Lógica específica para Miembros
    if (titulo == "LISTA DE MIEMBROS" or "MIEMBROS INSCRITOS" in titulo) and lista and all(
            k in lista[0] for k in datos.CAMPOS_MIEMBROS):
        tabla.add_column("ID", justify="center", style="yellow")
        tabla.add_column("Nombre", justify="left", style="white")
        tabla.add_column("Suscripción", justify="center", style="magenta")

        for item in lista:
            suscripcion = item.get('tipo_suscripcion', '')
            color = "green" if suscripcion == "Anual" else "blue"
            tabla.add_row(
                item.get('id_miembro', ''),
                item.get('nombre', ''),
                f"[{color}]{suscripcion}[/{color}]"
            )

    # Lógica específica para Clases
    elif (titulo == "LISTA DE CLASES" or "CLASES DE MIEMBRO" in titulo) and lista and all(
            k in lista[0] for k in datos.CAMPOS_CLASES):
        tabla.add_column("ID", justify="center", style="yellow")
        tabla.add_column("Clase", justify="left", style="white")
        tabla.add_column("Instructor", justify="left", style="blue")
        tabla.add_column("Cupo Máximo", justify="center", style="magenta")

        for item in lista:
            cupo_max = item.get('cupo_maximo', '0')
            tabla.add_row(
                item.get('id_clase', ''),
                item.get('nombre_clase', ''),
                item.get('instructor', ''),
                cupo_max
            )

    # Lógica para otras tablas (Inscripciones sin detalles de Miembro/Clase) o el caso genérico
    else:
        # Usar la lógica genérica original si no es Miembros o Clases
        for key in lista[0].keys():
            tabla.add_column(key, justify="center")

        for item in lista:
            tabla.add_row(*[str(v) for v in item.values()])

    console.print(tabla)


# ============================================================
# MENÚ DE MIEMBROS
# ============================================================

def menu_miembros():
    while True:
        menu_content = (
            "[bold cyan]*** GESTIÓN DE MIEMBROS ***[/bold cyan]\n"
            "1. Registrar nuevo miembro\n"
            "2. Ver todos los miembros\n"
            "3. Actualizar datos de miembro\n"
            "4. Eliminar miembro\n"
            "\n"
            "0. Volver al menú principal"
        )
        panel_menu = Panel(menu_content, border_style="bold cyan", padding=(1, 2))
        console.print(panel_menu)

        opcion = Prompt.ask("Seleccione una opción", choices=["0", "1", "2", "3", "4"], show_choices=False)

        if opcion == "0":
            break

        elif opcion == "1":
            nombre = Prompt.ask("Nombre completo")
            tipo = solicitar_tipo_suscripcion()
            miembro = crud.crear_miembro(MIEMBROS_FILE, nombre, tipo)
            if miembro:
                console.print(f"[green]Miembro creado con éxito (ID {miembro['id_miembro']}).[/green]")
            pausar()

        elif opcion == "2":
            miembros = crud.leer_todos_los_miembros(MIEMBROS_FILE)
            mostrar_tabla(miembros, "LISTA DE MIEMBROS")
            pausar()

        elif opcion == "3":
            id_miembro = Prompt.ask("Ingrese el ID del miembro a actualizar")
            miembro = crud.buscar_miembro_por_id(MIEMBROS_FILE, id_miembro)
            if not miembro:
                console.print("[red]Miembro no encontrado.[/red]")
                pausar()
                continue

            # MEJORA DE USABILIDAD
            console.print(
                f"\nEditando miembro: [cyan]{miembro['nombre']}[/cyan] (Suscripción actual: {miembro['tipo_suscripcion']})")
            nuevo_nombre = Prompt.ask("Nuevo nombre (dejar vacío para no cambiar)", default="")

            # Se usa la función que permite seleccionar o no cambiar
            console.print("\n[bold]--- TIPO DE SUSCRIPCIÓN ---[/bold]")
            nuevo_tipo = solicitar_tipo_suscripcion(permitir_vacio=True)

            datos_nuevos = {}
            if nuevo_nombre.strip():
                datos_nuevos["nombre"] = nuevo_nombre
            if nuevo_tipo:
                datos_nuevos["tipo_suscripcion"] = nuevo_tipo

            actualizado = crud.actualizar_miembro(MIEMBROS_FILE, id_miembro, datos_nuevos)
            if actualizado:
                console.print("[green]Miembro actualizado con éxito.[/green]")
            else:
                console.print("[red]No se pudo actualizar el miembro.[/red]")
            pausar()

        elif opcion == "4":
            id_miembro = Prompt.ask("Ingrese el ID del miembro a eliminar")
            exito = crud.eliminar_miembro(MIEMBROS_FILE, id_miembro, INSCRIPCIONES_FILE)
            if exito:
                console.print("[green]Miembro e inscripciones eliminadas con éxito.[/green]")
            else:
                console.print("[red]No se encontró el miembro especificado.[/red]")
            pausar()


# ============================================================
# MENÚ DE CLASES
# ============================================================

def menu_clases():
    while True:
        menu_content = (
            "[bold cyan]*** GESTIÓN DE CLASES ***[/bold cyan]\n"
            "1. Registrar nueva clase\n"
            "2. Ver todas las clases\n"
            "3. Ver cupos disponibles\n"
            "\n"
            "0. Volver al menú principal"
        )
        panel_menu = Panel(menu_content, border_style="bold blue", padding=(1, 2))
        console.print(panel_menu)

        opcion = Prompt.ask("Seleccione una opción", choices=["0", "1", "2", "3"], show_choices=False)

        if opcion == "0":
            break

        elif opcion == "1":
            nombre = Prompt.ask("Nombre de la clase")
            instructor = Prompt.ask("Nombre del instructor")
            cupo = Prompt.ask("Cupo máximo")

            try:
                cupo = int(cupo)
            except ValueError:
                console.print("[red]El cupo debe ser un número.[/red]")
                pausar()
                continue

            clase = crud.crear_clase(CLASES_FILE, nombre, instructor, cupo)
            if clase:
                console.print(f"[green]Clase creada con éxito (ID {clase['id_clase']}).[/green]")
            pausar()

        elif opcion == "2":
            clases = crud.leer_todas_las_clases(CLASES_FILE)
            mostrar_tabla(clases, "LISTA DE CLASES")
            pausar()

        elif opcion == "3":
            # La función ver_cupos_disponibles en crud.py ya usa rich.table
            crud.ver_cupos_disponibles()
            pausar()


# ============================================================
# MENÚ DE INSCRIPCIONES
# ============================================================

from rich.panel import Panel


# ... (otras importaciones y código)

# ============================================================
# MENÚ DE INSCRIPCIONES
# ============================================================

def menu_inscripciones():
    while True:
        menu_content = (
            "[bold cyan]*** GESTIÓN DE INSCRIPCIONES ***[/bold cyan]\n"
            "1. Inscribir miembro en clase\n"
            "2. Dar de baja miembro de clase\n"
            "3. Ver miembros inscritos en una clase\n"
            "4. Ver clases inscritas por miembro\n"
            "\n"
            "0. Volver al menú principal"
        )
        panel_menu = Panel(menu_content, border_style="bold magenta", padding=(1, 2))
        console.print(panel_menu)

        opcion = Prompt.ask("Seleccione una opción", choices=["0", "1", "2", "3", "4"], show_choices=False)

        if opcion == "0":
            break

        elif opcion == "1":
            # --- Validaciones para Inscribir ---
            while True:
                id_miembro = Prompt.ask("ID del miembro").strip()
                if id_miembro: break
                console.print("[red]Error:[/red] El ID del miembro no puede estar vacío. Intente de nuevo.")

            while True:
                id_clase = Prompt.ask("ID de la clase").strip()
                if id_clase: break
                console.print("[red]Error:[/red] El ID de la clase no puede estar vacío. Intente de nuevo.")

            exito, mensaje = crud.inscribir_miembro_en_clase(INSCRIPCIONES_FILE, CLASES_FILE, id_miembro, id_clase)
            color = "green" if exito else "red"
            console.print(f"[{color}]{mensaje}[/{color}]")
            pausar()

        elif opcion == "2":
            # --- Validaciones para Dar de Baja ---
            while True:
                id_miembro = Prompt.ask("ID del miembro").strip()
                if id_miembro: break
                console.print("[red]Error:[/red] El ID del miembro no puede estar vacío. Intente de nuevo.")

            while True:
                id_clase = Prompt.ask("ID de la clase").strip()
                if id_clase: break
                console.print("[red]Error:[/red] El ID de la clase no puede estar vacío. Intente de nuevo.")

            exito = crud.dar_baja_miembro_de_clase(INSCRIPCIONES_FILE, id_miembro, id_clase)
            if exito:
                console.print("[green]Baja realizada correctamente.[/green]")
            else:
                console.print("[red]No se encontró la inscripción especificada.[/red]")
            pausar()

        elif opcion == "3":
            # --- Validación para Ver Miembros ---
            while True:
                id_clase = Prompt.ask("Ingrese ID de la clase").strip()
                if id_clase: break
                console.print("[red]Error:[/red] El ID de la clase no puede estar vacío. Intente de nuevo.")

            clase = crud.buscar_clase_por_id(CLASES_FILE, id_clase)
            clase_nombre = clase['nombre_clase'] if clase else id_clase

            miembros = crud.listar_miembros_inscritos_en_clase(INSCRIPCIONES_FILE, MIEMBROS_FILE, id_clase)
            mostrar_tabla(miembros, f"MIEMBROS INSCRITOS EN CLASE '{clase_nombre}'")
            pausar()

        elif opcion == "4":
            # --- Validación para Ver Clases ---
            while True:
                id_miembro = Prompt.ask("Ingrese ID del miembro").strip()
                if id_miembro: break
                console.print("[red]Error:[/red] El ID del miembro no puede estar vacío. Intente de nuevo.")

            clases = crud.listar_clases_inscritas_por_miembro(INSCRIPCIONES_FILE, CLASES_FILE, id_miembro)
            mostrar_tabla(clases, f"CLASES DE MIEMBRO ID {id_miembro}")
            pausar()

# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def menu_principal():
    while True:
        menu_content = (
            "[bold yellow] SISTEMA DE GESTIÓN DE GIMNASIO [/bold yellow]\n"
            "1. Gestión de Miembros\n"
            "2. Gestión de Clases\n"
            "3. Gestión de Inscripciones\n"
            "\n"
            "0. Salir"
        )
        panel_menu = Panel(menu_content, border_style="bold yellow", padding=(1, 2))
        console.print(panel_menu)

        opcion = Prompt.ask("Seleccione una opción", choices=["0", "1", "2", "3"], show_choices=False)

        if opcion == "0":
            console.print("[green]¡Hasta luego![/green]")
            break
        elif opcion == "1":
            menu_miembros()
        elif opcion == "2":
            menu_clases()
        elif opcion == "3":
            menu_inscripciones()


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    # Crear carpeta info/ si no existe
    os.makedirs(INFO_DIR, exist_ok=True)

    # Llama a la nueva función en datos.py
    datos.inicializar_archivos(MIEMBROS_FILE, CLASES_FILE, INSCRIPCIONES_FILE)

    menu_principal()