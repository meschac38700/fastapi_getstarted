from http import HTTPStatus
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.security.csrf import get_csrf_protect
from core.templating.loaders import app_template_loader
from settings import settings


def render_string(
    request: Request, template_name: str, context: dict[str, Any] = None
) -> str:
    """Render application template with given context in string format."""
    _context = context or {}
    template = Jinja2Templates(None, env=app_template_loader)
    return template.get_template(template_name).render({**_context, "request": request})


def render(
    request: Request,
    template_name: str,
    context: dict[str, Any] = None,
    status_code: HTTPStatus = HTTPStatus.OK,
) -> HTMLResponse:
    """Return HTMLResponse of the template with given context."""
    csrf_protect = get_csrf_protect()
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens(settings.secret_key)

    _context = context or {}
    _context.update({settings.token_key: csrf_token})

    response = HTMLResponse(
        render_string(request, template_name, _context), status_code
    )

    csrf_protect.set_csrf_cookie(signed_token, response)
    return response
