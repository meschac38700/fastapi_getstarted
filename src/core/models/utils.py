import logging
from copy import deepcopy
from typing import Any, Optional, TypeVar

import pydantic_core
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

BaseModelT = TypeVar("BaseModelT", bound=BaseModel)

logger = logging.getLogger(__name__)

# Context: https://github.com/pydantic/pydantic/issues/3120#issuecomment-1528030416


def optional_fields(model: type[BaseModelT]) -> type[BaseModelT]:
    def make_field_optional(
        field: FieldInfo, default: Any = None
    ) -> tuple[Any, FieldInfo]:
        new = deepcopy(field)
        if not isinstance(field.default, pydantic_core.PydanticUndefinedType):
            new.default = field.default
        else:
            new.default = default
        new.annotation = Optional[field.annotation]
        return new.annotation, new

    return create_model(
        f"Partial{model.__name__}",
        __base__=model,
        __module__=model.__module__,
        **{
            field_name: make_field_optional(field_info)
            for field_name, field_info in model.model_fields.items()
        },
    )
