# -*- coding: utf-8 -*-
"""
Sistema de gestión de gimnasio
--------------------------------
Permite administrar miembros, clases e inscripciones.
"""

import os
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

import crud
import datos

console = Console()

INFO_DIR = "info"
MIEMBROS_FILE = os.path.join(INFO_DIR, "miembros.csv")
CLASES_FILE = os.path.join(INFO_DIR, "clases.csv")
INSCRIPCIONES_FILE = os.path.join(INFO_DIR, "inscripciones.json")


def solicitar_tipo_suscripcion(permitir_vacio: bool = False) -> Optional[str]:
    """
    Muestra un menú para que el usuario elija el tipo de suscripción.

    :param permitir_vacio: Si es True, incluye la opción '0. No cambiar'.
    :return: Tipo de suscripción o None si el usuario elige no cambiar.
    """
    console.print("\nSeleccione el tipo de suscripción:", style="cyan")

    tipos = {"1": "Mensual", "2": "Anual"}

    opciones = list(tipos.keys())
    for key, value in tipos.items():
        console.print(f"{key}. {value}")

    if permitir_vacio:
        console.print("0. No cambiar")
        opciones.insert(0, "0")

    opcion = Prompt.ask("Opción", choices=opciones, show_choices=False)

    if permitir_vacio and opcion == "0":
        return None
    return tipos.get(opcion)


def pausar():
    input("\nPresione [Enter] para continuar...")


def mostrar_tabla(lista, titulo):
    """Muestra una lista de diccionarios en formato de tabla con estilo mejorado."""
    if not lista:
        console.print("[yellow]No hay datos para mostrar.[/yellow]")
        return

    tabla = Table(
        title=f"[bold green]{titulo}[/bold green]", style="cyan", show_lines=True
    )

    # Lógica específica para Miembros
    if (
        (titulo == "LISTA DE MIEMBROS" or "MIEMBROS INSCRITOS" in titulo)
        and lista
        and all(k in lista[0] for k in datos.CAMPOS_MIEMBROS)
    ):
        tabla.add_column("ID", justify="center", style="yellow")
        tabla.add_column("Nombre", justify="left", style="white")
        tabla.add_column("Suscripción", justify="center", style="magenta")

        for item in lista:
            suscripcion = item.get("tipo_suscripcion", "")
            color = "green" if suscripcion == "Anual" else "blue"
            tabla.add_row(
                item.get("id_miembro", ""),
                item.get("nombre", ""),
                f"[{color}]{suscripcion}[/{color}]",
            )

    # Lógica específica para Clases
    elif (
        (titulo == "LISTA DE CLASES" or "CLASES DE MIEMBRO" in titulo)
        and lista
        and all(k in lista[0] for k in datos.CAMPOS_CLASES)
    ):
        tabla.add_column("ID", justify="center", style="yellow")
        tabla.add_column("Clase", justify="left", style="white")
        tabla.add_column("Instructor", justify="left", style="blue")
        tabla.add_column("Cupo Máximo", justify="center", style="magenta")

        for item in lista:
            cupo_max = item.get("cupo_maximo", "0")
            tabla.add_row(
                item.get("id_clase", ""),
                item.get("nombre_clase", ""),
                item.get("instructor", ""),
                cupo_max,
            )

    else:
        for key in lista[0].keys():
            tabla.add_column(key, justify="center")

        for item in lista:
            tabla.add_row(*[str(v) for v in item.values()])

    console.print(tabla)


def registrar_miembro():
    """Opción 1: Registrar un nuevo miembro."""
    nombre = Prompt.ask("Nombre completo")
    tipo = solicitar_tipo_suscripcion()
    miembro = crud.crear_miembro(MIEMBROS_FILE, nombre, tipo)
    if miembro:
        console.print(f"[green]Miembro creado con éxito (ID {miembro['id_miembro']})."
                      f"[/green]")
    pausar()


def ver_todos_los_miembros():
    """Opción 2: Ver todos los miembros."""
    miembros = crud.leer_todos_los_miembros(MIEMBROS_FILE)
    mostrar_tabla(miembros, "LISTA DE MIEMBROS")
    pausar()


def actualizar_miembro():
    """Opción 3: Actualizar datos de un miembro con confirmación antes de guardar."""
    id_miembro = Prompt.ask("Ingrese el ID del miembro a actualizar")
    miembro = crud.buscar_miembro_por_id(MIEMBROS_FILE, id_miembro)
    if not miembro:
        console.print("[red]Miembro no encontrado.[/red]")
        pausar()
        return

    console.print(
        f"\nEditando miembro: [cyan]{miembro['nombre']}[/cyan] "
        f"(Suscripción actual: {miembro['tipo_suscripcion']})"
    )

    nuevo_nombre = Prompt.ask("Nuevo nombre (dejar vacío para no cambiar)", default="")
    console.print("\n[bold]--- TIPO DE SUSCRIPCIÓN ---[/bold]")
    nuevo_tipo = solicitar_tipo_suscripcion(permitir_vacio=True)

    datos_nuevos = {}
    if nuevo_nombre.strip():
        datos_nuevos["nombre"] = nuevo_nombre
    if nuevo_tipo:
        datos_nuevos["tipo_suscripcion"] = nuevo_tipo

    if not datos_nuevos:
        console.print("[yellow]No se realizaron cambios.[/yellow]")
        pausar()
        return

    console.print("\n[bold cyan]Resumen de cambios propuestos:[/bold cyan]")
    for campo, valor in datos_nuevos.items():
        valor_actual = miembro.get(campo, "(sin valor previo)")
        console.print(f" - {campo}: [yellow]{valor_actual}[/yellow] → [green]{valor}[/green]")

    confirmar = Prompt.ask(
        "\n¿Desea aplicar estos cambios? (S/N)",
        choices=["S", "N", "s", "n"],
        show_choices=False,
    ).lower()

    if confirmar != "s":
        console.print("[cyan]Actualización cancelada por el usuario.[/cyan]")
        pausar()
        return

    actualizado = crud.actualizar_miembro(MIEMBROS_FILE, id_miembro, datos_nuevos)
    if actualizado:
        console.print("[green]Miembro actualizado con éxito.[/green]")
    else:
        console.print("[red]No se pudo actualizar el miembro.[/red]")
    pausar()


def eliminar_miembro():
    """Opción 4: Eliminar miembro con confirmación doble."""
    id_miembro = Prompt.ask("Ingrese el ID del miembro a eliminar").strip()
    miembro = crud.buscar_miembro_por_id(MIEMBROS_FILE, id_miembro)

    if not miembro:
        console.print("[red]No se encontró el miembro especificado.[/red]")
        pausar()
        return

    nombre = miembro.get("nombre", "Desconocido")
    console.print(f"\n[bold yellow]Miembro encontrado:[/bold yellow] {nombre} (ID: {id_miembro})")

    confirmar = Prompt.ask(
        f"¿Está seguro que desea eliminar a [red]{nombre}[/red]? (S/N)",
        choices=["S", "N", "s", "n"],
        show_choices=False,
    ).lower()

    if confirmar != "s":
        console.print("[cyan]Operación cancelada.[/cyan]")
        pausar()
        return

    exito = crud.eliminar_miembro(MIEMBROS_FILE, id_miembro, INSCRIPCIONES_FILE)
    if exito:
        console.print("[green]Miembro e inscripciones eliminadas con éxito.[/green]")
    else:
        console.print("[red]Error: No se pudo eliminar el miembro.[/red]")
    pausar()



def menu_miembros():
    """Menú principal de gestión de miembros."""
    opciones = {
        "1": registrar_miembro,
        "2": ver_todos_los_miembros,
        "3": actualizar_miembro,
        "4": eliminar_miembro,
    }

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

        opcion = Prompt.ask("Seleccione una opción", choices=["0", "1", "2", "3", "4"],
                            show_choices=False)

        if opcion == "0":
            break
        accion = opciones.get(opcion)
        if accion:
            accion()



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

        opcion = Prompt.ask(
            "Seleccione una opción", choices=["0", "1", "2", "3"], show_choices=False
        )

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
                console.print(
                    f"[green]Clase creada con éxito (ID {clase['id_clase']}).[/green]"
                )
            pausar()

        elif opcion == "2":
            clases = crud.leer_todas_las_clases(CLASES_FILE)
            mostrar_tabla(clases, "LISTA DE CLASES")
            pausar()

        elif opcion == "3":
            crud.ver_cupos_disponibles()
            pausar()


def solicitar_id(tipo: str) -> str:
    """Solicita un ID no vacío."""
    while True:
        id_valor = Prompt.ask(f"ID del {tipo}").strip()
        if id_valor:
            return id_valor
        console.print(f"[red]Error:[/red] El ID del {tipo} no puede estar vacío.")

def inscribir_miembro():
    """Opción 1: Inscribir miembro en clase."""
    id_miembro = solicitar_id("miembro")
    miembro = crud.buscar_miembro_por_id(MIEMBROS_FILE, id_miembro)
    if not miembro:
        console.print(f"[red]Error:[/red] No existe ningún miembro con ID"
                      f" '{id_miembro}'.")
        pausar()
        return

    id_clase = solicitar_id("clase")
    clase = crud.buscar_clase_por_id(CLASES_FILE, id_clase)
    if not clase:
        console.print(f"[red]Error:[/red] No existe ninguna clase con ID '{id_clase}'.")
        pausar()
        return

    exito, mensaje = crud.inscribir_miembro_en_clase(
        INSCRIPCIONES_FILE, CLASES_FILE, id_miembro, id_clase
    )
    color = "green" if exito else "red"
    console.print(f"[{color}]{mensaje}[/{color}]")
    pausar()


def dar_baja_miembro():
    """Opción 2: Dar de baja un miembro de una clase."""
    id_miembro = solicitar_id("miembro")
    id_clase = solicitar_id("clase")

    exito = crud.dar_baja_miembro_de_clase(INSCRIPCIONES_FILE, id_miembro, id_clase)
    if exito:
        console.print("[green]Baja realizada correctamente.[/green]")
    else:
        console.print("[red]No se encontró la inscripción especificada.[/red]")
    pausar()


def ver_miembros_de_clase():
    """Opción 3: Ver miembros inscritos en una clase."""
    id_clase = solicitar_id("clase")
    clase = crud.buscar_clase_por_id(CLASES_FILE, id_clase)
    clase_nombre = clase["nombre_clase"] if clase else id_clase

    miembros = crud.listar_miembros_inscritos_en_clase(
        INSCRIPCIONES_FILE, MIEMBROS_FILE, id_clase
    )
    mostrar_tabla(miembros, f"MIEMBROS INSCRITOS EN CLASE '{clase_nombre}'")
    pausar()


def ver_clases_de_miembro():
    """Opción 4: Ver clases inscritas por miembro."""
    id_miembro = solicitar_id("miembro")
    clases = crud.listar_clases_inscritas_por_miembro(
        INSCRIPCIONES_FILE, CLASES_FILE, id_miembro
    )
    mostrar_tabla(clases, f"CLASES DE MIEMBRO ID {id_miembro}")
    pausar()


def menu_inscripciones():
    """Menú principal de gestión de inscripciones."""
    opciones = {
        "1": inscribir_miembro,
        "2": dar_baja_miembro,
        "3": ver_miembros_de_clase,
        "4": ver_clases_de_miembro,
    }

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

        opcion = Prompt.ask("Seleccione una opción", choices=["0", "1", "2", "3", "4"],
                            show_choices=False)

        if opcion == "0":
            break
        accion = opciones.get(opcion)
        if accion:
            accion()

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

        opcion = Prompt.ask(
            "Seleccione una opción", choices=["0", "1", "2", "3"], show_choices=False
        )

        if opcion == "0":
            console.print("[green]¡Hasta luego![/green]")
            break
        elif opcion == "1":
            menu_miembros()
        elif opcion == "2":
            menu_clases()
        elif opcion == "3":
            menu_inscripciones()


if __name__ == "__main__":
    os.makedirs(INFO_DIR, exist_ok=True)

    # Llama a la nueva función en datos.py
    datos.inicializar_archivos(MIEMBROS_FILE, CLASES_FILE, INSCRIPCIONES_FILE)

    menu_principal()
