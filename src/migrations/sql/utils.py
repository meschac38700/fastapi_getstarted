import re


def extract_table_name(statement: str) -> str | None:
    pattern = r'CREATE\s+TABLE\s+"?(?P<table_name>\w+)"?'
    res = re.search(pattern, statement, re.IGNORECASE)

    if res is None:
        return None

    return res.group("table_name")
