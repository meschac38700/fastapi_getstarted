import pytest

from apps.user.models import User
from core.unittest.async_case import AsyncTestCase


class TestQueryOperators(AsyncTestCase):
    fixtures = ["users"]

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

    async def test_invalid_operator_error(self):
        with pytest.raises(ValueError) as e:
            await User.filter(is__equality="test")
        assert str(e.value) == "Invalid operator: equality"

    async def test_get_equals(self):
        pk = 1
        u = await User.get(id=pk)
        assert isinstance(u, User)
        assert u.id == pk

        u1 = await User.get(id__equals=pk)
        assert u == u1

    async def test_filter_not_equals(self):
        pk = 1
        users = await User.filter(id__not_equals=pk)
        assert pk not in [u.id for u in users]

    async def test_filter_equals(self):
        pk = 1
        u = await User.get(id=pk)
        assert isinstance(u, User)
        assert u.id == pk

    async def test_filter_in(self):
        ids = [1, 2]
        users = await User.filter(id__in=ids)
        assert len(ids) == len(users)
        assert ids == [u.id for u in users]

    async def test_filter_not_in(self):
        ids = [1, 2]
        users = await User.filter(id__not_in=ids)
        actual_ids = [u.id for u in users]
        assert ids != actual_ids
        assert all(pk not in actual_ids for pk in ids)

    async def test_filter_less_than(self):
        pk = 1
        users = await User.filter(id__lt=pk)
        assert all(pk > u.id for u in users)

    async def test_filter_less_or_equals(self):
        pk = 1
        users = await User.filter(id__lte=pk)
        assert all(pk >= u.id for u in users)

    async def test_filter_greater_than(self):
        pk = 1
        users = await User.filter(id__gt=pk)
        assert all(pk < u.id for u in users)

    async def test_filter_greater_or_equals(self):
        pk = 1
        users = await User.filter(id__gte=pk)
        assert all(pk <= u.id for u in users)

    async def test_filter_contains(self):
        email_domain = "example.com"
        users = await User.filter(email__contains=email_domain)
        assert all(user.email.endswith(email_domain) for user in users)

    async def test_filter_icontains(self):
        email_domain = "example.com".upper()
        users = await User.filter(email__contains=email_domain)
        assert [] == users

        users = await User.filter(email__icontains=email_domain)
        assert all(user.email.upper().endswith(email_domain) for user in users)

    async def test_filter_not_contains(self):
        term = "doe"

        users = await User.filter(email__not_contains=term)
        assert all(term not in user.email for user in users)

    async def test_filter_not_icontains(self):
        term = "DoE"

        users = await User.filter(email__not_icontains=term)
        assert all(term not in user.email for user in users)

    async def test_filter_startswith(self):
        term = "Pyt"
        users = await User.filter(last_name__startswith=term.lower())
        assert [] == users

        users = await User.filter(last_name__startswith=term)
        assert len(users) >= 1
        assert all(user.last_name.startswith(term) for user in users)

    async def test_filter_istartswith(self):
        term = "Pyt"
        users = await User.filter(last_name__istartswith=term.lower())
        assert len(users) >= 1
        assert all(user.last_name.startswith(term) for user in users)

    async def test_filter_endswith(self):
        term = "API"
        users = await User.filter(last_name__endswith=term.lower())
        assert [] == users

        users = await User.filter(last_name__endswith=term)
        assert len(users) >= 1
        assert all(user.last_name.endswith(term) for user in users)

    async def test_filter_iendswith(self):
        term = "API"
        users = await User.filter(last_name__iendswith=term.lower())
        assert len(users) >= 1
        assert all(user.last_name.endswith(term) for user in users)
