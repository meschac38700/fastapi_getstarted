from http import HTTPStatus
from pathlib import Path

from core.templating import utils as http_utils


def test_get_render_template_as_string(http_request, template_dir: Path):
    index_file = template_dir / "index.html"

    expected_text = "<h1>render template: {{template_name}}</h1>"
    index_file.write_text(expected_text)

    template_content = http_utils.render_string(
        http_request, index_file.name, context={"template_name": index_file.name}
    )

    assert template_content == expected_text.replace(
        "{{template_name}}", index_file.name
    )


def test_get_render_template_as_html_response(http_request, template_dir: Path):
    index_file = template_dir / "index.html"

    expected_text = "<h1>render template: {{template_name}}</h1>"
    index_file.write_text(expected_text)

    html_response = http_utils.render(
        http_request, index_file.name, context={"template_name": index_file.name}
    )

    assert HTTPStatus.OK == html_response.status_code
    assert expected_text.replace(
        "{{template_name}}", index_file.name
    ) == html_response.body.decode("utf-8")
