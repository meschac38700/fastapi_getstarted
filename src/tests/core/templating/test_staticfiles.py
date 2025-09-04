from pathlib import Path

from fastapi import status


async def test_load_static_file_in_template(
    static_root: Path, template_dir, setup_test_routes, client, app_url
):
    css_filename = "styles.css"
    css_file = static_root / css_filename
    css_file.write_text("html, body {color: red;}")

    css_html_link = (
        "<link href=\"{{ url_for('static', path='/"
        + css_filename
        + '\') }}" rel="stylesheet" />'
    )

    index_file = template_dir / "index.html"
    index_file.write_text(css_html_link)

    response = await client.get(setup_test_routes)

    assert response.status_code == status.HTTP_200_OK
    expected_html_link = f'<link href="{app_url}/static/styles.css" rel="stylesheet" />'
    assert expected_html_link == response.content.decode("utf-8")
