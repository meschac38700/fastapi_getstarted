from sqlmodel import SQLModel

from core.services import files

app_metadata = [
    SQLModel.metadata,
]

globals().update({model.__name__: model for model in files.retrieve_all_app_models()})

__all__ = [
    "app_metadata",
]
