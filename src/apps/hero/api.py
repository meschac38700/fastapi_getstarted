from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Query
from sqlmodel import select

from core.db import SessionDep

from .models import Hero

router = APIRouter(tags=["heroes"])


@router.get("/", name="Get heroes")
async def get_items(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    heroes = await session.exec(select(Hero).offset(offset).limit(limit))
    return heroes.all()
