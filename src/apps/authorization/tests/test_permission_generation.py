import re

from apps.authorization.models import Permission
from apps.hero.models import Hero
from core.unittest.async_case import AsyncTestCase


class TestPermissionGeneration(AsyncTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.perms = [
            Permission.format_permission_name("create", Hero.table_name()),
            Permission.format_permission_name("read", Hero.table_name()),
            Permission.format_permission_name("update", Hero.table_name()),
            Permission.format_permission_name("delete", Hero.table_name()),
        ]

    async def test_generate_hero_permissions(self):
        await Permission.generate_crud_objects(Hero.table_name())

        hero_crud_perms = await Permission.filter(target_table=Hero.table_name())
        assert 4 == len(hero_crud_perms)

        actual_perm_names = [perm.name for perm in hero_crud_perms]
        assert actual_perm_names == self.perms
        assert all(perm.target_table == Hero.table_name() for perm in hero_crud_perms)

    async def test_get_permission_insert_raw_sql(self):
        actual_sql = Permission.get_crud_data_list(Hero.table_name(), raw_sql=True)
        expected_sql = f"""INSERT INTO permission(name, description, display_name, target_table)
            VALUES('{self.perms[0]}', 'This permission allows user to create the Hero model.', 'Create hero', 'hero'),
            ('{self.perms[1]}', 'This permission allows user to read the Hero model.', 'Read hero', 'hero'),
            ('{self.perms[2]}', 'This permission allows user to update the Hero model.', 'Update hero', 'hero'),
            ('{self.perms[3]}', 'This permission allows user to delete the Hero model.', 'Delete hero', 'hero');
        """
        actual_sql = re.sub("\\s+|\n+", "", actual_sql)
        expected_sql = re.sub("\\s+|\n+", "", expected_sql)
        assert actual_sql == expected_sql
