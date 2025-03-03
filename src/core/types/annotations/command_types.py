from typing import Annotated, TypeAlias

import typer


def TyperListOption(description: str, of_type: type = str) -> TypeAlias:  # noqa: N802
    return Annotated[
        list[of_type],
        typer.Option(
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
