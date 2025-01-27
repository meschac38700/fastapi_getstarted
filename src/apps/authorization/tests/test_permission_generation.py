import re

from apps.authorization.models.permission import Permission
from apps.hero.models import Hero
from core.test.async_case import AsyncTestCase


class TestPermissionGeneration(AsyncTestCase):
    async def test_generate_hero_permissions(self):
        # TODO(Eliam): The following line of code is needed just when we run the tests outside the Docker container
        #  Alembic migration should automatically generate all permissions
        #  but as we are manually initializing the database, the alembic code is not executed
        await Permission.generate_crud_permissions(Hero.table_name())

        hero_crud_perms = await Permission.filter(
            Permission.target_table == Hero.table_name()
        )
        self.assertEqual(4, len(hero_crud_perms))
        expected_perm_names = [
            "create_hero",
            "read_hero",
            "update_hero",
            "delete_hero",
        ]
        actual_perm_names = [perm.name for perm in hero_crud_perms]
        self.assertListEqual(actual_perm_names, expected_perm_names)
        self.assertTrue(
            all(perm.target_table == Hero.table_name() for perm in hero_crud_perms)
        )

    async def test_get_permission_insert_raw_sql(self):
        actual_sql = Permission.get_model_crud_permissions(
            Hero.table_name(), raw_sql=True
        )
        expected_sql = """INSERT INTO permission(name, description, display_name, target_table)
            VALUES('create_hero', 'This permission allows user to create any Hero instance.', 'Create hero', 'hero'),
            ('read_hero', 'This permission allows user to read any Hero instance.', 'Read hero', 'hero'),
            ('update_hero', 'This permission allows user to update any Hero instance.', 'Update hero', 'hero'),
            ('delete_hero', 'This permission allows user to delete any Hero instance.', 'Delete hero', 'hero');
        """
        actual_sql = re.sub("\\s+|\n+", "", actual_sql)
        expected_sql = re.sub("\\s+|\n+", "", expected_sql)
        self.assertEqual(actual_sql, expected_sql)
