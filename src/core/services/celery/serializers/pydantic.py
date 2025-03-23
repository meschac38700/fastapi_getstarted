import json

from fastapi.encoders import jsonable_encoder
from kombu.serialization import register
from pydantic import BaseModel
from sqlmodel import SQLModel

import apps


class PydanticSerializer(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return jsonable_encoder(o) | {"__type__": type(o).__name__}

        return super().default(o)


def find_model_by_name(model_name: str) -> SQLModel | None:
    if model_name not in apps.__dict__:
        return None
    return apps.__dict__[model_name]


def pydantic_decoder(obj: BaseModel) -> SQLModel | BaseModel:
    if "__type__" in obj:
        klass = find_model_by_name(obj["__type__"])
        if klass is not None:
            return klass.model_validate(obj)
    return obj


def pydantic_encode(obj: BaseModel):
    return json.dumps(obj, cls=PydanticSerializer)


# Decoder function
def pydantic_decode(obj: BaseModel):
    return json.loads(obj, object_hook=pydantic_decoder)


def register_pydantic_serializer() -> str:
    # Register new serializer methods into kombu
    register_name = "pydantic"
    register(
        register_name,
        pydantic_encode,
        pydantic_decode,
        content_type="application/x-pydantic",
        content_encoding="utf-8",
    )
    return register_name
