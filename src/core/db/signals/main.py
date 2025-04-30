from importlib import import_module

from core.services.files import (
    get_application_paths,
    linux_path_to_module_path,
)


def setup_signals():
    """Import all the signals declared in each application in the "apps" folder.

    Importing them will automatically apply a listener to each declared event.
    """

    app_paths = get_application_paths(required_module="signals")
    for app_path in app_paths:
        module_path = linux_path_to_module_path(app_path / "signals")
        import_module(module_path)
