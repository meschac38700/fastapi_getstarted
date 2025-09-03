import pytest
from fastapi import status
from playwright.async_api import Page

from apps.user.models import User


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.E2E
async def test_redirect_to_login_view(
    app, page: Page, e2e_base_url: str, settings
) -> None:
    login_url = e2e_base_url + app.url_path_for("session-login")
    response = await page.goto(e2e_base_url)

    assert response.status == status.HTTP_200_OK

    expected_url = login_url + f"?referer={settings.session_auth_redirect_success}"
    assert response.url == expected_url
    assert page.url == expected_url

    form = page.locator("form")
    assert await form.count() == 1
    assert await form.get_attribute("method") == "POST"
    assert await form.get_attribute("action") == login_url

    csrf_input = form.locator("input[name=csrf_token]")
    username_input = form.locator("input[name=username]")
    password_input = form.locator("input[name=password]")

    assert await csrf_input.count() == 1
    assert await csrf_input.get_attribute("name") == settings.token_key
    assert await csrf_input.get_attribute("type") == "hidden"
    assert len(await csrf_input.get_attribute("value")) > 1
    assert await username_input.count() == 1
    assert await password_input.count() == 1


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.E2E
async def test_user_login_workflow(
    app, page: Page, e2e_base_url: str, settings
) -> None:
    user = await User(
        username="e2e",
        first_name="DOE",
        last_name="Pytest",
        email="e2e.doe@example.org",
        password=(lambda: "password")(),
    ).save()

    login_url = e2e_base_url + app.url_path_for("session-login")
    response = await page.goto(login_url, wait_until="load")

    assert response.status == status.HTTP_200_OK
    form = page.locator("form")
    assert await form.count() == 1
    username_input = form.locator("input[name=username]")
    password_input = form.locator("input[name=password]")

    await username_input.fill(user.username)
    await password_input.fill("password")
    submit_button = form.locator("button[type='submit']")
    assert await submit_button.count() == 1

    await submit_button.click()
    expected_redirect_url = e2e_base_url + settings.session_auth_redirect_success
    assert page.url == expected_redirect_url
