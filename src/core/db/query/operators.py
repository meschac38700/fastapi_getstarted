from functools import lru_cache, partial
from typing import Any, Sequence

from sqlalchemy.sql._typing import ColumnExpressionArgument
from sqlmodel import col


class QueryExpressionManager:
    @classmethod
    @lru_cache
    def _operator_resolvers(cls):
        return {
            "contains": cls._contains,
            "icontains": partial(cls._contains, case_insensitive=True),
            "in": cls._in,
            "gt": cls._gt,
            "gte": partial(cls._gt, or_equals=True),
            "lt": cls._lt,
            "lte": partial(cls._lt, or_equals=True),
            "startswith": cls._startswith,
            "istartswith": partial(cls._startswith, case_insensitive=True),
            "endswith": cls._endswith,
            "iendswith": partial(cls._endswith, case_insensitive=True),
        }

    @classmethod
    def get_attribute(cls, name: str):
        try:
            return col(getattr(cls, name))
        except AttributeError as e:
            msg = (
                f"Model {cls.__name__} does not have any field named: '{name}'."
                f"\nPlease retry with one of: {tuple(cls.model_fields.keys())}'"
            )
            raise AttributeError(msg) from e

    @classmethod
    def resolve_filters(cls, **filters):
        _filters = []
        for key, value in filters.items():
            _key, sep, operator = key.partition("__")
            if sep and not operator:
                raise ValueError(f"Invalid operator: {key}")

            resolver = cls._operator_resolvers().get(operator, cls._equals)
            _filters.extend(resolver(**{_key: value}))
        return _filters

    @classmethod
    def _equals(
        cls, **filters: dict[str, Any]
    ) -> Sequence[ColumnExpressionArgument[bool] | bool]:
        return [cls.get_attribute(name) == value for name, value in filters.items()]

    @classmethod
    def _contains(
        cls, *, case_insensitive: bool = False, **filters
    ) -> Sequence[ColumnExpressionArgument[bool] | bool]:
        return [
            cls.get_attribute(name).icontains(value)
            if case_insensitive
            else cls.get_attribute(name).contains(value)
            for name, value in filters.items()
        ]

    @classmethod
    def _in(cls, **filters) -> Sequence[ColumnExpressionArgument[bool] | bool]:
        return [cls.get_attribute(name).in_(value) for name, value in filters.items()]

    @classmethod
    def _gt(
        cls, *, or_equals: bool = False, **filters
    ) -> Sequence[ColumnExpressionArgument[bool] | bool]:
        return [
            cls.get_attribute(name) >= value
            if or_equals
            else cls.get_attribute(name) > value
            for name, value in filters.items()
        ]

    @classmethod
    def _lt(
        cls, *, or_equals: bool = False, **filters
    ) -> Sequence[ColumnExpressionArgument[bool] | bool]:
        return [
            cls.get_attribute(name) <= value
            if or_equals
            else cls.get_attribute(name) < value
            for name, value in filters.items()
        ]

    @classmethod
    def _startswith(
        cls, *, case_insensitive: bool = False, **filters
    ) -> Sequence[ColumnExpressionArgument[bool] | bool]:
        return [
            cls.get_attribute(name).istartswith(value)
            if case_insensitive
            else cls.get_attribute(name).startswith(value)
            for name, value in filters.items()
        ]

    @classmethod
    def _endswith(
        cls, *, case_insensitive: bool = False, **filters
    ) -> Sequence[ColumnExpressionArgument[bool] | bool]:
        return [
            cls.get_attribute(name).iendswith(value)
            if case_insensitive
            else cls.get_attribute(name).endswith(value)
            for name, value in filters.items()
        ]
