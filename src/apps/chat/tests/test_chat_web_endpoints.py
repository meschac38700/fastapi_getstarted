import pytest
from fastapi import status

from apps.chat.models import ChatRoom
from apps.user.models import User


@pytest.fixture
async def rooms(db, user):  # pylint: disable=unused-argument
    rooms = [
        ChatRoom(name="Python developers", owner_id=user.id),
        ChatRoom(name="Javascript developers", owner_id=user.id),
        ChatRoom(name="PHP developers", owner_id=user.id),
        ChatRoom(name="Java developers", owner_id=user.id),
    ]
    await ChatRoom.bulk_create_or_update(rooms)
    return rooms


async def test_get_chat_template(client, app, user, csrf_token, settings):
    response = await client.get(app.url_path_for("chat-template"))
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    login_data = {
        "username": user.username,
        "password": (lambda: "password")(),
        settings.token_key: csrf_token,
    }
    response = await client.post(app.url_path_for("session-login"), data=login_data)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.next_request.url.path == settings.session_auth_redirect_success

    response = await client.get(app.url_path_for("chat-template"))
    assert response.status_code == status.HTTP_200_OK
    assert '<meta name="csrf_token" content=' in response.text
    assert '<div class="rooms">' in response.text


async def test_filter_rooms_with_owner(
    client, app, user, app_url, csrf_token, settings, rooms
):
    # session login
    login_data = {
        "username": user.username,
        "password": (lambda: "password")(),
        settings.token_key: csrf_token,
    }
    response = await client.post(app.url_path_for("session-login"), data=login_data)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.next_request.url.path == settings.session_auth_redirect_success

    # Query to filter rooms start with "java"
    query = {"room_name": "java"}
    url = (
        app.url_path_for("room-filter")
        .make_absolute_url(app_url)
        .include_query_params(**query)
    )
    response = await client.get(str(url))

    assert response.status_code == status.HTTP_200_OK
    actual = response.json()
    assert len(actual) == 2  # expecting Javascript developers AND Java developers
    expected = await ChatRoom.filter(name__istartswith="java")
    assert all(room.model_dump(mode="json") in response.json() for room in expected)

    # query filter without term
    response = await client.get(app.url_path_for("room-filter"))
    assert response.status_code == status.HTTP_200_OK
    actual = response.json()
    assert len(actual) == len(rooms)
    assert all(
        room.model_dump(mode="json") in response.json() for room in await ChatRoom.all()
    )


async def test_filter_rooms_with_admin(client, app, csrf_token, settings, admin, rooms):
    # session login with admin
    login_data = {
        "username": admin.username,
        "password": (lambda: "admin")(),
        settings.token_key: csrf_token,
    }
    response = await client.post(app.url_path_for("session-login"), data=login_data)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.next_request.url.path == settings.session_auth_redirect_success

    response = await client.get(app.url_path_for("room-filter"))
    # even though admin is not a member of any of these chat rooms or owner, he should be able to filter these rooms
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(rooms)
    expected = await ChatRoom.filter(name__istartswith="java")
    assert all(room.model_dump(mode="json") in response.json() for room in expected)


async def test_filter_rooms_with_lambda_user(client, app, csrf_token, settings, rooms):
    # Query filter with lambda user
    assert rooms
    user_lambda = await User(
        username="lambda",
        password=(lambda: "lambda")(),
        first_name="Lambda",
        last_name="DOE",
    ).save()
    login_data = {
        "username": user_lambda.username,
        "password": (lambda: "lambda")(),
        settings.token_key: csrf_token,
    }
    response = await client.post(app.url_path_for("session-login"), data=login_data)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.next_request.url.path == settings.session_auth_redirect_success

    response = await client.get(app.url_path_for("room-filter"))
    # Since the lambda is not admin, owner or member of any chat rooms
    assert response.status_code == status.HTTP_200_OK
    actual = response.json()
    assert len(actual) == 0
