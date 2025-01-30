#### FastAPI template project

#### Python Version:

###### *_python >= 3.13.X_*

# Get started

Rename the folder **envs.example** to **envs** Then change the environment
information

# Build Application environment

#### Install dependencies

We use
[uv](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) to
manage dependencies: The following command will install all project dependencies in a
virtual environment.

By default, uv will create a virtual env in a hidden folder named `.venv` if you want to
change the location and name, you can set
[UV_PROJECT_ENVIRONMENT](https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path)
as environment variable before running the following command.

```bash
uv sync --all-extras
```

Next we need to activate the virtual environment created by uv previously

```bash
source ./.venv/bin/activate
```

#### Setup `direnv`

> [!NOTE]
>
> This is optional but recommended to automatically export the environment variables
> needed to run the local server.
>
> direnv is an extension for your shell. It augments existing shells with a new feature
> that can load and unload environment variables depending on the current directory.

Get started with [direnv](https://direnv.net/#getting-started) Once direnv is installed
all you have to do is to allow the `.envrc` file

```bash
cd getstarted
direnv allow .
```

if you don't want to configure `direnv`, you need to export `APP_ENVIRONMENT` every time
you move to the project directory:

```bash
export APP_ENVIRONMENT=dev
```

## Run the application

Run prod server

```bash
docker compose up
```

Run development server
[TODO(Create command dev server)](https://github.com/meschac38700/fastapi_getstarted/issues/6)

```bash
docker compose -f docker-compose.dev.yaml up -d database-dev && fastapi dev src/main.py
```

#### Running migrations

We use [alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) to manage
migrations. The following commands, as explained in the documentation, will allow you to
create and run the migrations.

```bash
cd src
alembic revision --autogenerate -m "message of commit"
alembic upgrade heads
```

> [!WARNING]
> After adding a new application in the `apps/` module,
> you have to import the new model in the `apps/__init__.py`
> This will permit alembic to consider the new model during its migration process.
