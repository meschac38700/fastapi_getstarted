from unittest import TestCase

from apps.user.models import User
from apps.user.tasks.user import create_user_task


class TestCeleryTasks(TestCase):
    def test_create_user_task(self):
        user_data = {
            "username": "pytest",
            "first_name": "Celery",
            "last_name": "FastApi",
            "password": "test",
        }
        created_user = create_user_task.delay(**user_data).get(timeout=15)
        assert isinstance(created_user, User)
        assert created_user.first_name == user_data["first_name"]
        assert created_user.last_name == user_data["last_name"]
        assert created_user.username == user_data["username"]
        assert created_user.check_password(user_data["password"])
