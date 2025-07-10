from typing import Any

from core.templating.loaders import app_template_loader


def render(template_name: str, context: dict[str, Any] = None) -> str:
    """Render application template with given context."""
    return app_template_loader.get_template(template_name).render(**(context or {}))
