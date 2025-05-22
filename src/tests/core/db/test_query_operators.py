import pytest

from apps.user.models import User
from core.testing.async_case import AsyncTestCase


class TestQueryOperators(AsyncTestCase):
    fixtures = ["users"]

    async def asyncSetUp(self):
        await super().asyncSetUp()

    async def test_bad_operator(self):
        with pytest.raises(ValueError) as e:
            await User.filter(id__=1)

        assert str(e.value) == "Invalid operator: id__"

    async def test_attribute_error(self):
        with pytest.raises(AttributeError) as e:
            await User.filter(unknow_field="test")

        expected_msg = (
            f"Model {User.__name__} does not have any field named: 'unknow_field'."
            f"\nPlease retry with one of: {tuple(User.model_fields.keys())}'"
        )
        assert str(e.value) == expected_msg

    async def test_get_equals(self):
        pk = 1
        u = await User.get(id=pk)
        self.assertIsInstance(u, User)
        self.assertEqual(u.id, pk)
