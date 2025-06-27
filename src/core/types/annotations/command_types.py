from typing import Annotated

import typer


class TyperListOption:
    def __call__[U = str, T = list[U]](
        self, *param_decls: str, help_msg: str = "", of_type: U = str
    ) -> Annotated[T, typer.Option]:
        return Annotated[
            list[of_type],
            typer.Option(
                *param_decls,
                help=help_msg,
                default_factory=list,
            ),
        ]


typer_list_options = TyperListOption()


class TyperListArgument:
    def __call__[U = str, T = list[U]](
        self, help_msg: str = "", of_type: U = str
    ) -> Annotated[T, typer.Option]:
        return Annotated[
            list[of_type],
            typer.Argument(
                help=help_msg,
            ),
        ]


typer_list_arguments = TyperListArgument()
