from apps.user.models import User
from core.tasks import create_user_task


class TestCeleryTasks:
    def test_create_task(self):
        user_data = {
            "username": "pytest",
            "first_name": "Celery",
            "last_name": "FastApi",
            "password": "test",
        }

        user = create_user_task.delay(**user_data).get(timeout=15)
        assert isinstance(user, User)
        assert user.first_name == user_data["first_name"]
        assert user.last_name == user_data["last_name"]
        assert user.username == user_data["username"]
        assert user.password == user_data["password"]
