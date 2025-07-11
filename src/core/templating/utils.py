from http import HTTPStatus
from typing import Any

from starlette.responses import HTMLResponse

from core.templating.loaders import app_template_loader


def render_string(template_name: str, context: dict[str, Any] = None) -> str:
    """Render application template with given context in string format."""
    return app_template_loader.get_template(template_name).render(**(context or {}))


def render(
    template_name: str,
    context: dict[str, Any] = None,
    status_code: HTTPStatus = HTTPStatus.OK,
) -> HTMLResponse:
    """Return HTMLResponse of the template with given context."""
    return HTMLResponse(render_string(template_name, context), status_code)
