from core.db import SQLTable
from core.db.mixins import BaseTable


class MyTestModel(SQLTable, BaseTable, table=True):
    """For testing purposes."""

    name: str
