from typing import Annotated, TypeAlias

import typer


def TyperListOption(  # noqa: N802
    *param_decls: str, description: str, of_type: type = str
) -> TypeAlias:
    return Annotated[
        list[of_type],
        typer.Option(
            *param_decls,
            help=description,
            default_factory=list,
        ),
    ]


def TyperListArgument(description: str = "", of_type: type = str) -> TypeAlias:  # noqa: N802
    return Annotated[
        list[of_type],
        typer.Argument(
            help=description,
        ),
    ]
