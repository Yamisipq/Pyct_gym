from rich.console import Console

import main


def test_import_main_has_console():
    assert hasattr(main, "console")
    assert isinstance(main.console, Console.__class__) or hasattr(main.console, "print")
