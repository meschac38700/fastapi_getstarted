from http import HTTPStatus


async def test_redirect_user_using_referer(
    client, app, app_url, settings, user, csrf_token
):
    chat_url = app.url_path_for("chat-template")
    response = await client.get(chat_url, follow_redirects=True)
    referer = response.url.params.get("referer")

    assert response.status_code == HTTPStatus.OK
    assert referer == chat_url.make_absolute_url(app_url).path

    login_info = {
        "username": user.username,
        "password": (lambda: "password")(),
        settings.token_key: csrf_token,
    }
    response = await client.post(str(response.url), data=login_info)

    assert response.status_code == HTTPStatus.FOUND
    assert response.next_request.url.path == referer
