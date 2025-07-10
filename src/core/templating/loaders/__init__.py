from .apps import environment

app_template_loader = environment()

__all__ = [
    "app_template_loader",
]
