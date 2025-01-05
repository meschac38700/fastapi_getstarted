from apps.hero import routers as hero_routers

"""
the route data must respect the signature of the following function:
def include_router(self,
   router: APIRouter,
   *,
   prefix: str = "",
   tags: list[str | Enum] | None = None,
   dependencies: Sequence[Depends] | None = None,
   responses: dict[int | str, dict[str, Any]] | None = None,
   deprecated: bool | None = None,
   include_in_schema: bool = True,
   default_response_class: Type[Response] = Default(JSONResponse),
   callbacks: list[BaseRoute] | None = None,
   generate_unique_id_function: (APIRoute) -> str = Default(generate_unique_id)
) -> None
"""
app_routers = [
    {"router": hero_routers.routers, "prefix": "/heroes"},
]
