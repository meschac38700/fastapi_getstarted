import pytest
from fastapi import FastAPI, status

from apps.chat.models import ChatMessage, ChatRoom
from apps.user.models import User
from core.unittest.client import AsyncClientTest


@pytest.fixture
async def subscriber(db):  # pylint: disable=unused-argument
    return await User(
        username="j.subscriber",
        first_name="John",
        last_name="Subscriber",
        email="john.sub@example.org",
        password=(lambda: "subscriber")(),
    ).save()


@pytest.fixture
async def jane(subscriber, db):  # pylint: disable=unused-argument
    return await User(
        username="j.user",
        first_name="Jane",
        last_name="DOE",
        email="jane.doe@example.org",
        password=(lambda: "subscriber")(),
    ).save()


@pytest.fixture()
async def room(db, user: User):  # pylint: disable=unused-argument
    return await ChatRoom(name="my-chat-room", owner=user).save()


@pytest.fixture
async def chat_message(db, subscriber, room: ChatRoom) -> ChatMessage:  # pylint: disable=unused-argument
    return await ChatMessage(
        content="Hello World!", author=subscriber, room=room
    ).save()


async def test_get_chat_rooms(
    client: AsyncClientTest,
    app: FastAPI,
    admin: User,
    subscriber: User,
    room: ChatRoom,
):
    response = await client.get(app.url_path_for("room-all"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    await client.user_login(subscriber)
    response = await client.get(app.url_path_for("room-all"))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Insufficient rights to carry out this action"}

    await client.force_login(admin)
    response = await client.get(app.url_path_for("room-all"))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "items": [room.model_dump(mode="json")],
        "total": 1,
        "page": 1,
        "size": 50,
        "pages": 1,
    }


async def test_get_chat_room(
    client: AsyncClientTest,
    room: ChatRoom,
    app: FastAPI,
    user: User,
    subscriber: User,
):
    response = await client.get(app.url_path_for("room-get", room_id=room.id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    await client.user_login(subscriber)
    response = await client.get(app.url_path_for("room-get", room_id=room.id))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Insufficient rights to carry out this action"}

    await client.force_login(user)
    response = await client.get(app.url_path_for("room-get", room_id=-1))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Object {ChatRoom.__name__} not found."}

    response = await client.get(app.url_path_for("room-get", room_id=room.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == room.model_dump(mode="json")


@pytest.mark.usefixtures("db")
async def test_get_room_messages_forbidden(
    client: AsyncClientTest, room, subscriber, app: FastAPI
):
    response = await client.get(app.url_path_for("room-messages", room_id=room.id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    await client.user_login(subscriber)
    response = await client.get(app.url_path_for("room-messages", room_id=room.id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures("db")
async def test_get_room_messages_by_subscriber(
    client: AsyncClientTest,
    room: ChatRoom,
    subscriber: User,
    chat_message: ChatMessage,
    app: FastAPI,
):
    await client.user_login(subscriber)

    response = await client.get(app.url_path_for("room-messages", room_id=room.id))
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await room.subscribe(subscriber)

    # Not found
    response = await client.get(app.url_path_for("room-messages", room_id=-1))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Object {ChatRoom.__name__} not found."}

    # Success
    response = await client.get(app.url_path_for("room-messages", room_id=room.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "items": [chat_message.model_dump(mode="json")],
        "total": 1,
        "page": 1,
        "size": 50,
        "pages": 1,
    }


@pytest.mark.usefixtures("db")
async def test_get_room_messages_by_chat_owner(
    client: AsyncClientTest,
    room: ChatRoom,
    user: User,
    chat_message: ChatMessage,
    app: FastAPI,
):
    await client.user_login(user)

    # Success
    response = await client.get(app.url_path_for("room-messages", room_id=room.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "items": [chat_message.model_dump(mode="json")],
        "total": 1,
        "page": 1,
        "size": 50,
        "pages": 1,
    }


@pytest.mark.usefixtures("db")
async def test_add_message_to_chat_room(
    client: AsyncClientTest,
    room: ChatRoom,
    app: FastAPI,
    subscriber: User,
):
    data = {"content": "John says: hello everybody."}

    await client.user_login(subscriber)
    response = await client.post(
        app.url_path_for("room-message-add", room_id=room.id), json=data
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Insufficient rights to carry out this action"}

    await room.subscribe(subscriber)

    # Not found
    response = await client.post(
        app.url_path_for("room-message-add", room_id=-1), json=data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Object {ChatRoom.__name__} not found."}

    # Success
    response = await client.post(
        app.url_path_for("room-message-add", room_id=room.id), json=data
    )
    assert response.status_code == status.HTTP_200_OK

    await room.refresh()

    created_message = await ChatMessage.get(room=room, content=data["content"])
    assert created_message in room.messages

    assert response.json() == created_message.model_dump(mode="json")


@pytest.mark.usefixtures("db")
async def test_delete_message_from_chat_room(
    client: AsyncClientTest,
    room: ChatRoom,
    chat_message: ChatMessage,
    app: FastAPI,
    subscriber: User,
    user: User,
    admin: User,
):
    # Not authorized
    response = await client.delete(
        app.url_path_for(
            "room-message-delete", room_id=room.id, message_id=chat_message.id
        ),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Forbidden for a room owner
    await client.user_login(user)

    response = await client.delete(
        app.url_path_for(
            "room-message-delete", room_id=room.id, message_id=chat_message.id
        ),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await client.force_login(subscriber)

    # Not found
    response = await client.delete(
        app.url_path_for("room-message-delete", room_id=-1, message_id=chat_message.id),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Object {ChatRoom.__name__} not found."}

    # Success by message author
    response = await client.delete(
        app.url_path_for(
            "room-message-delete", room_id=room.id, message_id=chat_message.id
        ),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    await room.refresh()
    assert room.messages == []

    # Success by admin
    msg = await ChatMessage(
        room_id=room.id, content="Hello everybody.", author_id=user.id
    ).save()
    await room.refresh()
    assert len(room.messages) == 1
    assert room.messages[0].id == msg.id

    await client.force_login(admin)
    response = await client.delete(
        app.url_path_for("room-message-delete", room_id=room.id, message_id=msg.id),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    await room.refresh()
    assert room.messages == []


async def test_user_subscribes_to_a_room(
    room: ChatRoom, subscriber: User, client: AsyncClientTest, app: FastAPI
) -> None:
    assert len(room.members) == 0

    # Unauthorize
    response = await client.patch(app.url_path_for("room-subscribe", room_id=room.id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    await client.user_login(subscriber)

    # Not found
    response = await client.patch(
        app.url_path_for("room-subscribe", room_id=-1),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Object {ChatRoom.__name__} not found."}

    # Success
    response = await client.patch(app.url_path_for("room-subscribe", room_id=room.id))
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {"success": True}

    await room.refresh()
    assert len(room.members) == 1


async def test_user_unsubscribes_to_a_room(
    room: ChatRoom, subscriber, client: AsyncClientTest, app: FastAPI
) -> None:
    await room.subscribe(subscriber)
    assert len(room.members) == 1

    response = await client.patch(app.url_path_for("room-unsubscribe", room_id=room.id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    await client.user_login(subscriber)

    # Not found
    response = await client.patch(
        app.url_path_for("room-unsubscribe", room_id=-1),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Object {ChatRoom.__name__} not found."}

    # Success
    response = await client.patch(app.url_path_for("room-unsubscribe", room_id=room.id))
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {"success": True}

    await room.refresh()
    assert len(room.members) == 0


async def test_create_chat_room(
    client: AsyncClientTest, user: User, app: FastAPI
) -> None:
    data = {"name": "my lovely friends"}
    response = await client.post(app.url_path_for("room-create"), json=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    await client.user_login(user)
    response = await client.post(app.url_path_for("room-create"), json=data)
    assert response.status_code == status.HTTP_201_CREATED
    created_chat_room = await ChatRoom.get(name=data["name"])
    assert response.json() == created_chat_room.model_dump(mode="json")


async def test_create_chat_room_error_already_exists(
    client: AsyncClientTest, user: User, admin: User, app: FastAPI
) -> None:
    chat_room = await ChatRoom(name="test", owner_id=user.id).save()
    assert chat_room.id is not None

    await client.user_login(user)
    response = await client.post(
        app.url_path_for("room-create"), json={"name": chat_room.name}
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "Chat room already exists."}

    # Should pass even though it's the same chat room name, we are another user
    await client.force_login(admin)
    response = await client.post(
        app.url_path_for("room-create"), json={"name": chat_room.name}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert await ChatRoom.get(name=chat_room.name, owner_id=admin.id) is not None


async def test_edit_chat_room(
    client: AsyncClientTest,
    subscriber: User,
    admin: User,
    user: User,
    room: ChatRoom,
    app: FastAPI,
) -> None:
    data = {"name": room.name + " Edited !"}
    response = await client.patch(
        app.url_path_for("room-edit", room_id=room.id), json=data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # forbidden: Owner or admin only
    await client.user_login(subscriber)
    response = await client.patch(
        app.url_path_for("room-edit", room_id=room.id), json=data
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Insufficient rights to carry out this action"}

    await client.force_login(user)
    response = await client.patch(
        app.url_path_for("room-edit", room_id=room.id), json=data
    )
    await room.refresh()

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {**room.model_dump(mode="json"), "name": data["name"]}

    # Test with admin user
    data = {"name": "admin room"}
    await client.force_login(admin)
    response = await client.patch(
        app.url_path_for("room-edit", room_id=room.id), json=data
    )
    await room.refresh()

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {**room.model_dump(mode="json"), "name": data["name"]}


async def test_delete_chat_room(
    client: AsyncClientTest, room: ChatRoom, user: User, subscriber: User, app: FastAPI
) -> None:
    # Unauthorize
    response = await client.delete(
        app.url_path_for("room-delete", room_id=room.id),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    await client.user_login(subscriber)

    # Forbidden
    response = await client.delete(
        app.url_path_for("room-delete", room_id=room.id),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Insufficient rights to carry out this action"}

    await client.force_login(user)

    # Not found
    response = await client.delete(
        app.url_path_for("room-delete", room_id=-1),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Object {ChatRoom.__name__} not found."}

    # Success
    response = await client.delete(
        app.url_path_for("room-delete", room_id=room.id),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await ChatRoom.get(id=room.id) is None
