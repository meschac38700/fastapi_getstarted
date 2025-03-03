from typing import Annotated

import typer

import settings
from core.commands.utils.runners.server import DevServer
from core.services.docker.compose import DockerComposeManager

app = typer.Typer(rich_markup_mode="rich")


@app.command(help="Run development server.")
def server(
    port: Annotated[
        int, typer.Option(help="The port of the server. Default 8000.")
    ] = 8000,
    host: Annotated[
        str, typer.Option(help="The host of the server. Default localhost.")
    ] = "127.0.0.1",
    reload: Annotated[
        bool,
        typer.Option(help="Enable auto-reload of the server when (code) files change."),
    ] = True,
    force: Annotated[
        bool, typer.Option(help="Force recreating docker containers. Default False.")
    ] = False,
):
    dk_file = settings.BASE_DIR.parent / "docker-compose.dev.yaml"

    server_runner = DevServer(port=port, host=host, reload=reload)

    docker_manager = DockerComposeManager(dk_file, env="dev")

    docker_manager.run_process(server_runner, force_recreate=force)
